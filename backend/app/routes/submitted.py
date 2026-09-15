from flask import request,jsonify,Blueprint
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone
from app.database import db
from app.models import Exercise,Profile,Submit_Exercise,User,SubmissionStatusEnum
from flask_jwt_extended import get_jwt_identity,jwt_required
from app.eveluator.ai_evaluator import evaluator_ai

submitted = Blueprint("submitted",__name__)


@submitted.route('/post_exercise/<string:exercise_id>', methods=['POST'])
@jwt_required()
def post_exercise(exercise_id):
    user_id = get_jwt_identity()

    profile = Profile.query.filter_by(user_id=user_id).first()

    if not profile:
        return jsonify({
            "message": "You must have a profile to submit an exercise"
        }), 403

    exercise = Exercise.query.get_or_404(exercise_id)

    if not request.is_json:
        return jsonify({
            "message": "Request must be JSON"
        }), 400

    # check for a prior passing submission BEFORE calling the AI evaluator —
    # no point spending an external API call on something already solved.
    previous_submit = Submit_Exercise.query.filter_by(
        user_id=user_id,
        exercise_id=exercise_id,
        is_completed=True
    ).first()

    if previous_submit:
        return jsonify({
            'message': "exercise has been solved by you"
        }), 409

    title = exercise.title
    description = exercise.description
    xp_points = exercise.xp_points

    data = request.get_json()
    answer = data.get("answer", "").strip()

    if not answer:
        return jsonify({
            "message": "Answer is required"
        }), 400

    question = {
        "title": title,
        "description": description,
        "answer": answer
    }

    submission = Submit_Exercise(
        user_id=user_id,
        exercise_id=exercise.id,
        answer=answer,
        status=SubmissionStatusEnum.evaluating
    )
    db.session.add(submission)
    db.session.commit()

    try:
        result = evaluator_ai(param=question)
    except Exception:
        submission.status = SubmissionStatusEnum.failed
        db.session.commit()
        return jsonify({
            "message": "Evaluation failed, please try again",
            "submission": submission.to_dict()
        }), 502

    is_completed = result['passed']
    score = xp_points if is_completed else 0

    submission.status = SubmissionStatusEnum.completed
    submission.score = score
    submission.feedback = result['feedback']
    submission.is_completed = is_completed
    submission.completed_at = datetime.now(timezone.utc)

    if is_completed:
        # keep the denormalized XP total in sync in the same transaction
        # as the submission, so profile views never need a SUM() query.
        user = User.query.get(user_id)
        user.total_xp = (user.total_xp or 0) + score

    db.session.commit()

    return jsonify({
        "message": "Exercise submitted successfully",
        "submission": submission.to_dict()
    }), 201
    
    
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