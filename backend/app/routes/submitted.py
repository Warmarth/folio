from flask import request,jsonify,Blueprint
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone
from app.database import db
from app.models import Exercise,Profile,Submit_Exercise,User,SubmissionStatusEnum
from app.services.submit_exercise_service import (SubmitExerciseService,DuplicateSubmissionError,ProfileRequiredError,EvaluationError)

from flask_jwt_extended import get_jwt_identity,jwt_required
# from app.eveluator.ai_evaluator import evaluator_ai

submitted = Blueprint("submitted",__name__)


@submitted.route('/post_exercise/<string:exercise_id>', methods=['POST'])
@jwt_required()
def post_exercise(exercise_id):
    user_id = get_jwt_identity()

    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 400

    answer = (request.get_json().get("answer") or "").strip()
    if not answer:
        return jsonify({"message": "Answer is required"}), 400

    try:
        submission = SubmitExerciseService().submit(user_id, exercise_id, answer)
        return jsonify({
            "message": "Exercise submitted successfully",
            "submission": submission.to_dict(),
        }), 201
    except ProfileRequiredError:
        return jsonify({"message": "You must have a profile to submit an exercise"}), 403
    except DuplicateSubmissionError:
        return jsonify({"message": "exercise has been solved by you"}), 409
    except EvaluationError as e:
        return jsonify({
            "message": "Evaluation failed, please try again",
            "submission": e.submission.to_dict(),
        }), 502
    
    
@submitted.route('/submitted_exercise/<string:exercise_id>', methods=['GET'])
@jwt_required()
def get_solved_exercise(exercise_id):
    user_id = get_jwt_identity()

    if not user_id:
        return jsonify({
            "message": "Not an authenticated user"
        }), 401

    exercise = Submit_Exercise.query.filter_by(
        exercise_id=exercise_id,
        user_id=user_id,
        is_completed=True
    ).first()

    if not exercise:
        return jsonify({
            "message": "No completed submission found for this exercise"
        }), 404

    return jsonify({
        "data": exercise.to_dict()
    }), 200
    

@submitted.route('/submitted_exercise', methods=['GET'])
@jwt_required()
def mentor_get_submitted_exercise():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = min(per_page, 50)

    pagination = Submit_Exercise.query.options(
        joinedload(Submit_Exercise.user).joinedload(User.profile),
        joinedload(Submit_Exercise.exercise)
    ).order_by(
        Submit_Exercise.submitted_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "data": [s.to_dict() for s in pagination.items],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }
    }), 200