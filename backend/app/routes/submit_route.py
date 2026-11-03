from flask import request, jsonify, Blueprint, abort
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta, timezone
from app.database import db
from app.models import (Exercise, Profile, Submit_Exercise, User, SubmissionStatusEnum, RoleEnum, SubmissionMessage,MentorLearner, MentorLearnerStatusEnum)
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
LEVEL_ORDER = ("easy", "medium", "hard", "expert", "possible")


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


# ---------------------------------------------------------------------------
# The learner's Progress page.
# ---------------------------------------------------------------------------

def _as_utc(dt):
    if dt is None:
        return None
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def _iso(dt):
    dt = _as_utc(dt)
    return dt.isoformat() if dt else None


@submitted.route('/my_progress', methods=['GET'])
@jwt_required()
def my_progress():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    # Exercises this learner can do: those made by their active mentors. Anything they
    # have already submitted to still counts, even if the mentor link has since ended.
    mentor_ids = [
        link.mentor_id for link in
        MentorLearner.query.filter_by(learner_id=user_id, status=MentorLearnerStatusEnum.active).all()
    ]
    exercises = {}
    if mentor_ids:
        for e in Exercise.query.filter(Exercise.created_by.in_(mentor_ids)).all():
            exercises[e.id] = e

    graded = Submit_Exercise.query.filter(
        Submit_Exercise.user_id == user_id,
        Submit_Exercise.status == SubmissionStatusEnum.completed,
    ).options(joinedload(Submit_Exercise.exercise)).order_by(Submit_Exercise.submitted_at.desc()).all()
    for s in graded:
        exercises.setdefault(s.exercise_id, s.exercise)

    passed_ids = {s.exercise_id for s in graded if s.is_completed}
    attempted_ids = {s.exercise_id for s in graded}

    # By level
    by_level = {lvl: {"level": lvl, "total": 0, "completed": 0, "xp": 0} for lvl in LEVEL_ORDER}
    for e in exercises.values():
        row = by_level.get(e.level.value)
        if row is None:
            continue
        row["total"] += 1
        if e.id in passed_ids:
            row["completed"] += 1
            row["xp"] += e.xp_points

    # Tried but not passed yet (newest first, because `graded` is newest first)
    in_progress, seen = [], {}
    for s in graded:
        if s.exercise_id in passed_ids:
            continue
        results = s.test_results or []
        passed_tests = sum(1 for r in results if r.get("passed"))
        entry = seen.get(s.exercise_id)
        if entry is None:
            entry = seen[s.exercise_id] = {
                "exercise_id": s.exercise_id, "title": s.exercise.title, "level": s.exercise.level.value,
                "attempts": 0, "best_passed": 0, "total_tests": 0, "last_attempt_at": _iso(s.submitted_at),
            }
            in_progress.append(entry)
        entry["attempts"] += 1
        entry["best_passed"] = max(entry["best_passed"], passed_tests)
        entry["total_tests"] = max(entry["total_tests"], len(results))

    # XP per day for the last 14 days, and the day streak (days are in UTC)
    today = datetime.now(timezone.utc).date()
    xp_per_day, active_days = {}, set()
    for s in graded:
        active_days.add(_as_utc(s.submitted_at).date())
        if s.is_completed:
            day = _as_utc(s.completed_at or s.submitted_at).date()
            xp_per_day[day] = xp_per_day.get(day, 0) + (s.score or 0)
    xp_by_day = [
        {"date": (today - timedelta(days=i)).isoformat(), "xp": xp_per_day.get(today - timedelta(days=i), 0)}
        for i in range(13, -1, -1)
    ]
    day = today if today in active_days else today - timedelta(days=1)   # a streak survives until the day is over
    streak = 0
    while day in active_days:
        streak += 1
        day -= timedelta(days=1)

    return jsonify({"data": {
        "total_xp": user.total_xp or 0,
        "completed": len(passed_ids),
        "available": len(exercises),
        "success_rate": round(100 * len(passed_ids) / len(attempted_ids)) if attempted_ids else None,
        "streak_days": streak,
        "reviewed": sum(1 for s in graded if s.reviewed_at),
        "by_level": [by_level[lvl] for lvl in LEVEL_ORDER],
        "in_progress": in_progress[:5],
        "recent": [s.to_my_summary_dict() for s in graded[:8]],
        "xp_by_day": xp_by_day,
    }}), 200
    
# ---------------------------------------------------------------------------
# The mentor's Performance page: how the whole group is doing.
# ---------------------------------------------------------------------------
 
STUCK_AFTER_FAILED_ATTEMPTS = 3   # failed this many times without passing = stuck
INACTIVE_AFTER_DAYS = 7
_STATUS_ORDER = {"stuck": 0, "inactive": 1, "not_started": 2, "on_track": 3}
 
 
@submitted.route('/mentor/performance', methods=['GET'])
@jwt_required()
def mentor_performance():
    user_id = get_jwt_identity()
    if not _require_mentor(user_id):
        return jsonify({"message": "Only mentors can view performance"}), 403
 
    learner_ids = [
        link.learner_id for link in
        MentorLearner.query.filter_by(mentor_id=user_id, status=MentorLearnerStatusEnum.active).all()
    ]
    learners = User.query.filter(User.id.in_(learner_ids)).options(joinedload(User.profile)).all() if learner_ids else []
    exercises = Exercise.query.filter_by(created_by=user_id).all()
 
    # Graded submissions on THIS mentor's exercises, oldest first.
    graded = _mentor_submissions(user_id).filter(
        Submit_Exercise.status == SubmissionStatusEnum.completed
    ).options(joinedload(Submit_Exercise.exercise)).order_by(Submit_Exercise.submitted_at.asc()).all()
 
    # One entry per learner and exercise: how many tries, and whether (and when) they passed.
    pairs = {}
    last_active = {}
    for s in graded:
        p = pairs.setdefault((s.user_id, s.exercise_id), {"attempts": 0, "passed": False, "to_pass": None})
        p["attempts"] += 1
        if s.is_completed and not p["passed"]:
            p["passed"] = True
            p["to_pass"] = p["attempts"]
        last_active[s.user_id] = _as_utc(s.submitted_at)   # oldest first, so the last one wins
 
    now = datetime.now(timezone.utc)
    today = now.date()
    titles = {e.id: e.title for e in exercises}
 
    # --- learners ---
    learner_rows = []
    for u in learners:
        mine = {ex_id: p for (uid, ex_id), p in pairs.items() if uid == u.id}
        completed = sum(1 for p in mine.values() if p["passed"])
        xp = sum((s.score or 0) for s in graded if s.user_id == u.id and s.is_completed)
        seen = last_active.get(u.id)
        days_idle = (now - seen).days if seen else None
 
        stuck = [(ex_id, p["attempts"]) for ex_id, p in mine.items()
                 if not p["passed"] and p["attempts"] >= STUCK_AFTER_FAILED_ATTEMPTS]
        if stuck:
            ex_id, tries = max(stuck, key=lambda t: t[1])
            status, note = "stuck", f"Stuck on {titles.get(ex_id, 'an exercise')} ({tries} attempts)"
        elif days_idle is not None and days_idle >= INACTIVE_AFTER_DAYS:
            status, note = "inactive", f"No activity for {days_idle} days"
        elif not mine:
            status, note = "not_started", "Hasn't submitted anything yet"
        else:
            status, note = "on_track", "On track"
 
        learner_rows.append({
            "learner_id": u.id,
            "name": (u.profile.name if u.profile else None) or u.email,
            "status": status,
            "note": note,
            "completed": completed,
            "attempted": len(mine),
            "success_rate": round(100 * completed / len(mine)) if mine else None,
            "xp": xp,
            "last_active": _iso(seen),
        })
    learner_rows.sort(key=lambda r: (_STATUS_ORDER[r["status"]], -(datetime.fromisoformat(r["last_active"]).timestamp() if r["last_active"] else 0)))
 
    # --- exercises, hardest first ---
    exercise_rows = []
    for e in exercises:
        ps = [p for (uid, ex_id), p in pairs.items() if ex_id == e.id]
        passed = [p for p in ps if p["passed"]]
        exercise_rows.append({
            "exercise_id": e.id,
            "title": e.title,
            "level": e.level.value,
            "learners_attempted": len(ps),
            "learners_passed": len(passed),
            "pass_rate": round(100 * len(passed) / len(ps)) if ps else None,
            "avg_attempts_to_pass": round(sum(p["to_pass"] for p in passed) / len(passed), 1) if passed else None,
        })
    exercise_rows.sort(key=lambda r: (r["pass_rate"] is None, r["pass_rate"] if r["pass_rate"] is not None else 0, r["title"]))
 
    # --- activity: graded submissions per day, last 14 days ---
    per_day = {}
    for s in graded:
        day = _as_utc(s.submitted_at).date()
        bucket = per_day.setdefault(day, {"passed": 0, "failed": 0})
        bucket["passed" if s.is_completed else "failed"] += 1
    activity = []
    for i in range(13, -1, -1):
        day = today - timedelta(days=i)
        b = per_day.get(day, {"passed": 0, "failed": 0})
        activity.append({"date": day.isoformat(), **b})
 
    all_pairs = list(pairs.values())
    return jsonify({"data": {
        "learners": len(learner_ids),
        "exercises": len(exercises),
        "graded": len(graded),
        "pass_rate": round(100 * sum(1 for p in all_pairs if p["passed"]) / len(all_pairs)) if all_pairs else None,
        "xp_awarded": sum((s.score or 0) for s in graded if s.is_completed),
        "awaiting_review": _apply_filter(_mentor_submissions(user_id), "pending").count(),
        "learner_rows": learner_rows,
        "exercise_rows": exercise_rows,
        "activity": activity,
    }}), 200
 
 # ---------------------------------------------------------------------------
# The mentor's Learners page: everyone in the group, with their XP, and a way to remove them.
# ---------------------------------------------------------------------------
 
@submitted.route('/mentor/learners', methods=['GET'])
@jwt_required()
def mentor_learners():
    user_id = get_jwt_identity()
    if not _require_mentor(user_id):
        return jsonify({"message": "Only mentors can view their learners"}), 403
 
    learner_ids = [
        link.learner_id for link in
        MentorLearner.query.filter_by(mentor_id=user_id, status=MentorLearnerStatusEnum.active).all()
    ]
    learners = User.query.filter(User.id.in_(learner_ids)).options(joinedload(User.profile)).all() if learner_ids else []
    exercise_count = Exercise.query.filter_by(created_by=user_id).count()
 
    graded = _mentor_submissions(user_id).filter(
        Submit_Exercise.status == SubmissionStatusEnum.completed,
        Submit_Exercise.user_id.in_(learner_ids or [""]),
    ).all()
    passed, attempted, last_active = {}, {}, {}
    for s in graded:
        attempted.setdefault(s.user_id, set()).add(s.exercise_id)
        if s.is_completed:
            passed.setdefault(s.user_id, set()).add(s.exercise_id)
        seen = _as_utc(s.submitted_at)
        if s.user_id not in last_active or seen > last_active[s.user_id]:
            last_active[s.user_id] = seen
 
    rows = []
    for u in learners:
        profile = u.profile
        rows.append({
            "learner_id": u.id,
            "name": (profile.name if profile else None) or u.email,
            "email": u.email,
            "image_url": getattr(profile, "image_url", None) if profile else None,
            "xp": u.total_xp or 0,
            "completed": len(passed.get(u.id, ())),
            "attempted": len(attempted.get(u.id, ())),
            "last_active": _iso(last_active.get(u.id)),
        })
    rows.sort(key=lambda row: (-row["xp"], row["name"].lower()))   # most XP first
    return jsonify({"data": rows, "exercises": exercise_count}), 200
 
 
@submitted.route('/mentor/learners/<string:learner_id>', methods=['DELETE'])
@jwt_required()
def mentor_remove_learner(learner_id):
    """Takes a learner out of this mentor's group. Their own code, feedback and XP are kept."""
    user_id = get_jwt_identity()
    if not _require_mentor(user_id):
        return jsonify({"message": "Only mentors can remove learners"}), 403
 
    link = MentorLearner.query.filter_by(
        mentor_id=user_id, learner_id=learner_id, status=MentorLearnerStatusEnum.active
    ).first()
    if link is None:
        return jsonify({"message": "That learner is not in your group"}), 404
 
    db.session.delete(link)
    db.session.commit()
    return jsonify({"message": "Learner removed"}), 200