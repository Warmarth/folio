from flask import request, jsonify, Blueprint
from app.database import db
from app.models import User, Profile, RoleEnum
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.storage.r2 import upload_image, R2NotConfigured
from botocore.exceptions import ClientError, BotoCoreError

api = Blueprint('api', __name__)


def _paginate(query, order_col):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = min(per_page, 50)

    pagination = query.order_by(order_col.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return pagination, {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev
    }


def _create_profile_for_current_user(require_role=None):
    """Shared creation logic for both /create_profile and
    /mentors_create_profile. Images are no longer stored as raw bytes in
    the DB — the client uploads to object storage separately and just
    sends the resulting image_url here.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if require_role and user.role != require_role:
        return jsonify({"error": f"only {require_role.value}s can use this endpoint"}), 403

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    body = request.get_json()
    name = (body.get('name') or '').strip()
    bio = body.get('bio')
    expertise = body.get('expertise')
    image_url = body.get('image_url')

    if not name:
        return jsonify({"error": "field 'name' is required"}), 400

    if Profile.query.filter_by(user_id=user_id).first():
        return jsonify({"error": "profile already exists"}), 409

    profile = Profile(
        user_id=user_id,
        name=name,
        bio=bio,
        expertise=expertise,
        image_url=image_url
    )

    db.session.add(profile)
    db.session.commit()

    return jsonify({'data': profile.to_dict()}), 201


# === upload a profile image to R2, returns the public URL ===
# frontend flow: upload the file here first, then pass the returned
# image_url into /create_profile or /edit_profile.
@api.route('/upload_image', methods=['POST'])
@jwt_required()
def upload_profile_image():
    user_id = get_jwt_identity()

    file = request.files.get('image')
    if not file or not file.filename:
        return jsonify({"error": "no image file provided"}), 400

    try:
        image_url = upload_image(file, key_prefix=f"profile-images/{user_id}")
    except R2NotConfigured as e:
        return jsonify({"error": str(e)}), 503
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except (ClientError, BotoCoreError):
        return jsonify({"error": "image upload failed, please try again"}), 502

    return jsonify({"image_url": image_url}), 201


# === create profile (any role) ===
@api.route('/create_profile', methods=["POST"])
@jwt_required()
def create_profile_card():
    return _create_profile_for_current_user()


# === create profile, mentor-only alias (kept for existing frontend calls) ===
@api.route('/mentors_create_profile', methods=['POST'])
@jwt_required()
def create_mentors_profiles():
    return _create_profile_for_current_user(require_role=RoleEnum.mentor)


# === read own profile ===
@api.route('/profile', methods=['GET'])
@jwt_required()
def get_one():
    user_id = get_jwt_identity()

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    profile = Profile.query.filter_by(user_id=user_id).first()

    return jsonify({
        "email": user.email,
        "profile": profile.to_dict() if profile else None
    }), 200


# === same as above, mentor-facing alias ===
@api.route('/mentors_profile', methods=['GET'])
@jwt_required()
def get_mentors_profile():
    return get_one()


# === read all learner profiles (paginated, excludes self) ===
@api.route('/all_profile', methods=["GET"])
@jwt_required()
def get_all_profile():
    user_id = get_jwt_identity()

    query = Profile.query.join(User).filter(User.role == RoleEnum.learner, Profile.user_id != user_id)
    pagination, meta = _paginate(query, Profile.created_at)

    return jsonify({
        "data": [profile.to_dict() for profile in pagination.items],
        "pagination": meta
    }), 200


@api.route('/all_profile/<string:profile_id>', methods=['GET'])
def get_profile(profile_id):
    profile = Profile.query.get_or_404(profile_id, description="Profile not found")
    return jsonify({"data": profile.to_dict()}), 200


# === read all mentor profiles (paginated) ===
@api.route('/all_mentors', methods=['GET'])
@jwt_required()
def get_all_mentors():
    query = Profile.query.join(User).filter(User.role == RoleEnum.mentor)
    pagination, meta = _paginate(query, Profile.created_at)

    return jsonify({
        "data": [profile.to_dict() for profile in pagination.items],
        "pagination": meta
    }), 200


@api.route('/all_mentors/<string:mentor_id>', methods=['GET'])
@jwt_required()
def get_mentors_profile_by_id(mentor_id):
    profile = Profile.query.get_or_404(mentor_id, description="Mentor not found")
    return jsonify({"data": profile.to_dict()}), 200


# === all learners, paginated (kept as a separate named route for parity
# with the old API surface — same underlying query as /all_profile) ===
@api.route('/all_learner', methods=['GET'])
@jwt_required()
def all_learners():
    query = Profile.query.join(User).filter(User.role == RoleEnum.learner)
    pagination, meta = _paginate(query, Profile.created_at)

    return jsonify({
        "data": [profile.to_dict() for profile in pagination.items],
        "pagination": meta
    }), 200


# === update own profile ===
@api.route('/edit_profile', methods=['PATCH', 'PUT'])
@jwt_required()
def edit_profile():
    user_id = get_jwt_identity()
    profile = Profile.query.filter_by(user_id=user_id).first()

    if not profile:
        return jsonify({"error": "profile not found"}), 404

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    body = request.get_json()

    if not body:
        return jsonify({"error": "no data provided"}), 400

    updated = False

    if 'name' in body:
        name = (body.get('name') or '').strip()
        if not name:
            return jsonify({"error": "name cannot be empty"}), 400
        profile.name = name
        updated = True

    if 'bio' in body:
        profile.bio = body.get('bio')
        updated = True

    if 'expertise' in body:
        profile.expertise = body.get('expertise')
        updated = True

    if 'image_url' in body:
        profile.image_url = body.get('image_url')
        updated = True

    if updated:
        db.session.commit()

    return jsonify({
        "message": "profile updated" if updated else "no changes made",
        "data": profile.to_dict()
    }), 200


@api.route('/delete_user', methods=['DELETE'])
@jwt_required()
def delete_profile():
    user_id = get_jwt_identity()
    profile = Profile.query.filter_by(user_id=user_id).first()

    if not profile:
        return jsonify({"message": "user Profile not found"}), 404

    profile_id = profile.id
    db.session.delete(profile)
    db.session.commit()

    return jsonify({
        "id": profile_id,
        "message": "User profile succsefully deleted.",
    }), 200


@api.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "welcome to the de learner"
    }), 200