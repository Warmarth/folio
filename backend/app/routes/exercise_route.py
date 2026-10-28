from datetime import datetime, timedelta, timezone

from flask import request, jsonify, Blueprint
from app.database import db
from app.models import (
    Exercise, ExerciseTestCase, LanguageEnum,
    User, RoleEnum, LevelEnum, MentorLearner, MentorLearnerStatusEnum,
)
from flask_jwt_extended import jwt_required, get_jwt_identity

# creating the skeleton name for the exercise api
exercise = Blueprint('exercises', __name__)

LANGUAGES = {lang.value for lang in LanguageEnum}
CATEGORIES = {"programming", "frontend", "backend", "database", "design", "business", "other"}
MAX_TEXT_CHARS = 20_000


def valid_text(value, limit=MAX_TEXT_CHARS):
    return isinstance(value, str) and len(value) <= limit
MAX_TEST_CASES = 10
MAX_FIELD_CHARS = 10_000
MAX_STARTER_CHARS = 20_000


def parse_test_cases(raw):
    """Turns the JSON list from a mentor into ExerciseTestCase objects.
    Returns (cases, None) on success or (None, error_message) on bad input."""
    if not isinstance(raw, list):
        return None, "test_cases must be a list"
    if len(raw) > MAX_TEST_CASES:
        return None, f"an exercise can have at most {MAX_TEST_CASES} test cases"

    base = datetime.now(timezone.utc)
    cases = []
    for i, item in enumerate(raw):
        n = i + 1
        if not isinstance(item, dict):
            return None, f"test case {n} must be an object"
        stdin = item.get("stdin", "")
        expected = item.get("expected_output")
        hidden = item.get("is_hidden", True)
        if not isinstance(stdin, str) or not isinstance(expected, str):
            return None, f"test case {n}: stdin and expected_output must be text"
        if not isinstance(hidden, bool):
            return None, f"test case {n}: is_hidden must be true or false"
        if len(stdin) > MAX_FIELD_CHARS or len(expected) > MAX_FIELD_CHARS:
            return None, f"test case {n} is too large"
        cases.append(ExerciseTestCase(
            stdin=stdin,
            expected_output=expected,
            is_hidden=hidden,
            # explicit, increasing timestamps keep the mentor's order
            created_at=base + timedelta(microseconds=i),
        ))
    return cases, None


@exercise.route('/create_exercise', methods=['POST'])
@jwt_required()
def create_exercise():
    levels = ("easy", "medium", "hard", "expert", "possible")
    xp_map = {
        "easy": 2,
        "medium": 3,
        "hard": 5,
        "expert": 7,
        "possible": 9
    }

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or user.role != RoleEnum.mentor:
        return jsonify({
            "message": "you must have a mentor profile to create an exercise"
        }), 403

    if not request.is_json:
        return jsonify({
            "message": "Request must contain JSON data"
        }), 400

    data = request.get_json()

    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    level = data.get("level", "").strip()

    if not title or not description or not level:
        return jsonify({
            "message": "title, description and  level are required"
        }), 400

    if level not in levels:
        return jsonify({
            "message": "level not  found"
        }), 400

    # --- optional fields, so older clients keep working ---
    category = data.get("category", "other")
    if category not in CATEGORIES:
        return jsonify({"message": f"category must be one of: {', '.join(sorted(CATEGORIES))}"}), 400

    instructions = data.get("instructions", "")
    evaluation_criteria = data.get("evaluation_criteria", "")
    if not valid_text(instructions) or not valid_text(evaluation_criteria):
        return jsonify({"message": "instructions and evaluation_criteria must be text under 20,000 characters"}), 400

    language = data.get("language", "go")
    if language not in LANGUAGES:
        return jsonify({"message": f"language must be one of: {', '.join(sorted(LANGUAGES))}"}), 400

    starter_code = data.get("starter_code", "")
    if not isinstance(starter_code, str) or len(starter_code) > MAX_STARTER_CHARS:
        return jsonify({"message": "starter_code must be text under 20,000 characters"}), 400

    test_cases = []
    if "test_cases" in data:
        test_cases, error = parse_test_cases(data["test_cases"])
        if error:
            return jsonify({"message": error}), 400

    xp_points = xp_map[level]

    exe_card = Exercise(
        title=title,
        description=description,
        level=LevelEnum(level),
        xp_points=xp_points,
        category=category,
        instructions=instructions,
        evaluation_criteria=evaluation_criteria,
        language=LanguageEnum(language),
        starter_code=starter_code,
        test_cases=test_cases,
        created_by=user_id
    )
    db.session.add(exe_card)
    db.session.commit()

    return jsonify({
        "message": "Exercise created successfully",
        "exercise": exe_card.to_mentor_dict()
    }), 201


@exercise.route('/all_exercise', methods=['GET'])
@jwt_required()
def get_all_exercises():

    user_id = get_jwt_identity()
    mentor_relationships = MentorLearner.query.filter_by(learner_id=user_id, status=MentorLearnerStatusEnum.active).all()

    mentor_ids = [rel.mentor_id for rel in mentor_relationships]

    if not mentor_ids:
        return jsonify({
            "data": [],
            "pagination": {
                "page": 1,
                "per_page": 10,
                "total": 0,
                "pages": 0,
                "has_next": False,
                "has_prev": False
            }
        }), 200

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = min(per_page, 50)

    pagination = Exercise.query.filter(Exercise.created_by.in_(mentor_ids)).order_by(Exercise.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)

    return jsonify({
        "data": [exercise.to_dict() for exercise in pagination.items],   # learner-safe: no hidden tests
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }
    }), 200


@exercise.route('/all_exercise/<string:id>')
@jwt_required()
def get_one_exercise(id):

    user_id = get_jwt_identity()
    current_exe = Exercise.query.get_or_404(id)

    # The author sees every test; everyone else gets the learner-safe version.
    data = current_exe.to_mentor_dict() if current_exe.created_by == user_id else current_exe.to_dict()
    return jsonify({
        "data": data
    }), 200


@exercise.route('/all_exercise/<string:exercise_id>/update', methods=['PUT', 'PATCH'])
@jwt_required()
def update_exercise(exercise_id):

    user_id = get_jwt_identity()

    current_exe = Exercise.query.get_or_404(exercise_id)

    if current_exe.created_by != user_id:
        return jsonify({
            "message": "invalid action"
        }), 403

    if not request.is_json:
        return jsonify({'message': 'update must be of json type'}), 400

    xp_map = {
        "easy": 2,
        "medium": 3,
        "hard": 5,
        "expert": 7,
        "possible": 9
    }

    body = request.get_json()

    updated = False

    title = body.get('title', '').strip()
    description = body.get('description', '').strip()
    level = body.get('level', '').strip()

    if "title" in body and title:
        current_exe.title = title
        updated = True

    if "description" in body and description:
        current_exe.description = description
        updated = True

    if "level" in body:
        if level not in xp_map:
            return jsonify({
                "message": "Invalid level"
            }), 400
        current_exe.level = LevelEnum(level)
        current_exe.xp_points = xp_map[level]
        updated = True

    if "category" in body:
        if body["category"] not in CATEGORIES:
            return jsonify({"message": f"category must be one of: {', '.join(sorted(CATEGORIES))}"}), 400
        current_exe.category = body["category"]
        updated = True

    for field in ("instructions", "evaluation_criteria"):   # empty text is allowed: it clears the field
        if field in body:
            if not valid_text(body[field]):
                return jsonify({"message": f"{field} must be text under 20,000 characters"}), 400
            setattr(current_exe, field, body[field])
            updated = True

    # --- playground fields ---
    if "language" in body:
        if body["language"] not in LANGUAGES:
            return jsonify({"message": f"language must be one of: {', '.join(sorted(LANGUAGES))}"}), 400
        current_exe.language = LanguageEnum(body["language"])
        updated = True

    if "starter_code" in body:   # an empty string is allowed: it clears the starter code
        starter_code = body["starter_code"]
        if not isinstance(starter_code, str) or len(starter_code) > MAX_STARTER_CHARS:
            return jsonify({"message": "starter_code must be text under 20,000 characters"}), 400
        current_exe.starter_code = starter_code
        updated = True

    if "test_cases" in body:     # replaces the whole list of tests
        cases, error = parse_test_cases(body["test_cases"])
        if error:
            return jsonify({"message": error}), 400
        current_exe.test_cases = cases
        updated = True

    if updated:
        db.session.commit()

    return jsonify({
        "message": "exercise updated" if updated else "no changes made",
        "data": current_exe.to_mentor_dict()
    }), 200


@exercise.route('/all_exercise/<string:exercise_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_exercise(exercise_id):
    user_id = get_jwt_identity()
    exercise = Exercise.query.get_or_404(exercise_id)

    if exercise.created_by != user_id:
        return jsonify({
            "message": "invalid action,you are not the author of this exercise "
        }), 403

    exercise_title = exercise.title
    db.session.delete(exercise)   # its test cases are deleted with it
    db.session.commit()
    return jsonify({
        "message": f"succsefully deleted {exercise_title}"
    }), 204


@exercise.route('/all_exercise/mentor', methods=['GET'])
@jwt_required()
def get_exercises_by_mentor():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = min(per_page, 50)

    pagination = Exercise.query.filter_by(created_by=user_id).order_by(Exercise.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return {
        "data": [exercise.to_dict() for exercise in pagination.items],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }
    }