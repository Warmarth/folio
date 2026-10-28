from flask import request, jsonify, Blueprint, abort
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta, timezone
from app.database import db
from app.models import Exercise, Profile, Submit_Exercise, User, SubmissionStatusEnum, RoleEnum, SubmissionMessage
from app.services.submit_exercise_service import (SubmitExerciseService, DuplicateSubmissionError, ProfileRequiredError, EvaluationError)
from app.services.call_providers import call_links, enabled_providers, livekit_token, CallNotConfiguredError

from flask_jwt_extended import get_jwt_identity, jwt_required
# from app.eveluator.ai_evaluator import evaluator_ai

submitted = Blueprint("submitted", __name__)

# The mentor's filters. Every graded submission is in exactly one of pending / fail / done:
#   pending = tests passed, not reviewed yet     fail = tests not passed, not reviewed
#   done    = the mentor marked it reviewed
FILTERS = ("all", "pending", "fail", "done")
MAX_COMMENT_CHARS = 5000
MAX_MESSAGE_CHARS = 2000
MAX_MESSAGES_PER_MINUTE = 10   # per person, per submission


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


# ---------------------------------------------------------------------------
# Mentor side. A mentor only ever sees submissions of exercises they created.
# ---------------------------------------------------------------------------

def _mentor_submissions(user_id):
    return Submit_Exercise.query.join(
        Exercise, Submit_Exercise.exercise_id == Exercise.id
    ).filter(Exercise.created_by == user_id)


def _apply_filter(query, name):
    graded = Submit_Exercise.status == SubmissionStatusEnum.completed
    if name == "pending":
        return query.filter(graded, Submit_Exercise.is_completed.is_(True), Submit_Exercise.reviewed_at.is_(None))
    if name == "fail":
        return query.filter(graded, Submit_Exercise.is_completed.is_(False), Submit_Exercise.reviewed_at.is_(None))
    if name == "done":
        return query.filter(Submit_Exercise.reviewed_at.isnot(None))
    return query


def _require_mentor(user_id):
    user = User.query.get(user_id)
    return bool(user and user.role == RoleEnum.mentor)


def _owned_submission(submission_id, user_id):
    """The submission, if it belongs to one of this mentor's exercises. Otherwise a 404,
    so nobody can tell whether someone else's submission exists."""
    submission = Submit_Exercise.query.get_or_404(submission_id)
    if submission.exercise.created_by != user_id:
        abort(404)
    return submission


def _detail(submission):
    """Everything a mentor needs: the code, the feedback and each test with its input and
    expected output (hidden tests included)."""
    data = submission.to_mentor_dict()
    tests = {t.id: (n, t) for n, t in enumerate(submission.exercise.test_cases, start=1)}
    results = []
    for r in submission.test_results or []:
        number, test = tests.get(r.get("test_id"), (None, None))
        results.append({
            **r,
            "number": number,
            "stdin": test.stdin if test else None,
            "expected_output": test.expected_output if test else None,
        })
    data["test_results"] = results if submission.test_results is not None else None
    data["call"] = call_links(submission)
    return data


@submitted.route('/submitted_exercise', methods=['GET'])
@jwt_required()
def mentor_get_submitted_exercise():
    user_id = get_jwt_identity()
    if not _require_mentor(user_id):
        return jsonify({"message": "Only mentors can view submissions"}), 403

    name = request.args.get('filter', 'all')
    if name not in FILTERS:
        return jsonify({"message": f"filter must be one of: {', '.join(FILTERS)}"}), 400

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = min(per_page, 50)

    base = _mentor_submissions(user_id)
    pagination = _apply_filter(base, name).options(
        joinedload(Submit_Exercise.user).joinedload(User.profile),
        joinedload(Submit_Exercise.exercise)
    ).order_by(
        Submit_Exercise.submitted_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "data": [s.to_summary_dict() for s in pagination.items],
        "counts": {f: _apply_filter(base, f).count() for f in FILTERS},
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }
    }), 200


@submitted.route('/mentor/submission/<string:submission_id>', methods=['GET'])
@jwt_required()
def mentor_get_submission(submission_id):
    user_id = get_jwt_identity()
    if not _require_mentor(user_id):
        return jsonify({"message": "Only mentors can view submissions"}), 403
    return jsonify({"data": _detail(_owned_submission(submission_id, user_id))}), 200


@submitted.route('/mentor/submission/<string:submission_id>/review', methods=['POST'])
@jwt_required()
def mentor_review_submission(submission_id):
    user_id = get_jwt_identity()
    if not _require_mentor(user_id):
        return jsonify({"message": "Only mentors can review submissions"}), 403

    submission = _owned_submission(submission_id, user_id)
    if submission.status != SubmissionStatusEnum.completed:
        return jsonify({"message": "This submission has not been graded yet"}), 409

    comment = (request.get_json(silent=True) or {}).get("comment", "")
    if not isinstance(comment, str) or len(comment) > MAX_COMMENT_CHARS:
        return jsonify({"message": f"comment must be text under {MAX_COMMENT_CHARS} characters"}), 400

    submission.mentor_comment = comment.strip() or None
    submission.reviewed_at = datetime.now(timezone.utc)   # reviewing again just updates the comment
    db.session.commit()
    return jsonify({"message": "Submission reviewed", "data": _detail(submission)}), 200


# ---------------------------------------------------------------------------
# Learner side: their own reviewed code, and the chat with their mentor.
# ---------------------------------------------------------------------------

@submitted.route('/my_submissions', methods=['GET'])
@jwt_required()
def my_submissions():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)

    pagination = Submit_Exercise.query.filter(
        Submit_Exercise.user_id == user_id,
        Submit_Exercise.status == SubmissionStatusEnum.completed,   # graded ones only
    ).options(
        joinedload(Submit_Exercise.exercise)
    ).order_by(
        Submit_Exercise.submitted_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "data": [s.to_my_summary_dict() for s in pagination.items],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }
    }), 200


@submitted.route('/my_submissions/<string:submission_id>', methods=['GET'])
@jwt_required()
def my_submission(submission_id):
    user_id = get_jwt_identity()
    submission = Submit_Exercise.query.get_or_404(submission_id)
    if submission.user_id != user_id:
        abort(404)

    creator = submission.exercise.creator
    data = submission.to_dict()   # learner-safe: hidden tests show only pass or fail
    data["language"] = submission.exercise.language.value
    data["mentor_name"] = creator.profile.name if creator and creator.profile else None
    data["call"] = call_links(submission)
    return jsonify({"data": data}), 200


@submitted.route('/submission/<string:submission_id>/messages', methods=['GET', 'POST'])
@jwt_required()
def submission_messages(submission_id):
    """The chat for one submission. Only the learner and the exercise's mentor can use it."""
    user_id = get_jwt_identity()
    submission = Submit_Exercise.query.get_or_404(submission_id)
    if user_id not in (submission.user_id, submission.exercise.created_by):
        abort(404)

    if request.method == 'POST':
        body = (request.get_json(silent=True) or {}).get("body", "")
        if not isinstance(body, str) or not body.strip():
            return jsonify({"message": "Write a message first"}), 400
        if len(body) > MAX_MESSAGE_CHARS:
            return jsonify({"message": f"Messages can be up to {MAX_MESSAGE_CHARS} characters"}), 400

        recent = SubmissionMessage.query.filter(
            SubmissionMessage.submission_id == submission_id,
            SubmissionMessage.sender_id == user_id,
            SubmissionMessage.created_at >= datetime.now(timezone.utc) - timedelta(minutes=1),
        ).count()
        if recent >= MAX_MESSAGES_PER_MINUTE:
            return jsonify({"message": "You're sending messages too fast. Wait a moment."}), 429

        message = SubmissionMessage(submission_id=submission_id, sender_id=user_id, body=body.strip())
        db.session.add(message)
        db.session.commit()
        return jsonify({"data": message.to_dict(user_id)}), 201

    latest = SubmissionMessage.query.filter_by(submission_id=submission_id).order_by(
        SubmissionMessage.created_at.desc()
    ).limit(200).all()
    return jsonify({"data": [m.to_dict(user_id) for m in reversed(latest)]}), 200


@submitted.route('/submission/<string:submission_id>/call-token', methods=['POST'])
@jwt_required()
def submission_call_token(submission_id):
    """A pass to join this submission's call. Only used when livekit is in CALL_PROVIDERS."""
    user_id = get_jwt_identity()
    submission = Submit_Exercise.query.get_or_404(submission_id)
    if user_id not in (submission.user_id, submission.exercise.created_by):
        abort(404)

    if "livekit" not in enabled_providers():
        return jsonify({"message": "LiveKit calls are not turned on here, so there is no pass to create"}), 409

    mode = (request.get_json(silent=True) or {}).get("mode", "video")
    if mode not in ("video", "voice"):
        return jsonify({"message": "mode must be video or voice"}), 400

    user = User.query.get(user_id)
    name = user.profile.name if user and user.profile else None
    try:
        return jsonify({"data": livekit_token(submission, user_id, name, mode)}), 200
    except CallNotConfiguredError:
        return jsonify({"message": "Calls are not set up on this server yet"}), 503