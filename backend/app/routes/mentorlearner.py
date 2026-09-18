from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services import (
    request_mentor,
    accept_request,
    decline_request,
    end_relationship,
    get_relationship_status,
    get_startmentorship_request,
    MentorLearnerError,
)
from app.models import Profile


mentor_learner_bp = Blueprint("mentor_learner", __name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def resolve_profile(user_id: str):
    """Resolve a JWT user_id to their Profile, or None if it doesn't exist."""
    return Profile.query.filter_by(user_id=user_id).first()


# ---------------------------------------------------------------------------
# Create a request
# ---------------------------------------------------------------------------

@mentor_learner_bp.route("/<mentor_user_id>/request", methods=["POST"])
@jwt_required()
def request_mentor_service(mentor_user_id):
    """
    One smart POST: the service layer decides internally whether this is a
    brand new request or a reuse of an existing (declined/ended) row.
    The frontend never has to know or care which case it's in.
    """
    learner_profile = resolve_profile(get_jwt_identity())
    if not learner_profile:
        return jsonify({"error": "Learner profile not found"}), 404

    mentor_profile = resolve_profile(mentor_user_id)
    if not mentor_profile:
        return jsonify({"error": "Mentor profile not found"}), 404

    row = request_mentor(mentor_id=mentor_profile.id, learner_id=learner_profile.id)
    return jsonify(row.to_dict()), 200


# ---------------------------------------------------------------------------
# Respond to a request (mentor side)
# ---------------------------------------------------------------------------

@mentor_learner_bp.route("/<learner_id>/accept", methods=["PATCH"])
@jwt_required()
def accept_mentor_request(learner_id):
    mentor_profile = resolve_profile(get_jwt_identity())
    if not mentor_profile:
        return jsonify({"error": "Mentor profile not found"}), 404

    try:
        row = accept_request(mentor_profile.id, learner_id)
    except MentorLearnerError as e:
        return jsonify({"error": str(e)}), 409
    return jsonify(row.to_dict()), 200


@mentor_learner_bp.route("/<learner_id>/decline", methods=["PATCH"])
@jwt_required()
def decline_mentor_request(learner_id):
    mentor_profile = resolve_profile(get_jwt_identity())
    if not mentor_profile:
        return jsonify({"error": "Mentor profile not found"}), 404

    try:
        row = decline_request(mentor_profile.id, learner_id)
    except MentorLearnerError as e:
        return jsonify({"error": str(e)}), 409
    return jsonify(row.to_dict()), 200


# ---------------------------------------------------------------------------
# End an active relationship (either side)
# ---------------------------------------------------------------------------

@mentor_learner_bp.route("/<other_id>/end", methods=["PATCH"])
@jwt_required()
def end_mentor_relationship(other_id):
    caller_profile = resolve_profile(get_jwt_identity())
    if not caller_profile:
        return jsonify({"error": "Profile not found"}), 404

    try:
        row = end_relationship(caller_profile.id, other_id)
    except MentorLearnerError as e:
        return jsonify({"error": str(e)}), 409
    return jsonify(row.to_dict()), 200


# ---------------------------------------------------------------------------
# Read relationship state
# ---------------------------------------------------------------------------

@mentor_learner_bp.route("/<mentor_user_id>/status", methods=["GET"])
@jwt_required()
def get_mentor_relationship_status(mentor_user_id):
    learner_profile = resolve_profile(get_jwt_identity())
    if not learner_profile:
        return jsonify({"error": "Learner profile not found"}), 404

    mentor_profile = resolve_profile(mentor_user_id)
    if not mentor_profile:
        return jsonify({"error": "Mentor profile not found"}), 404

    row = get_relationship_status(mentor_profile.id, learner_profile.id)
    if row is None:
        return jsonify({"status": None}), 200
    return jsonify(row.to_dict()), 200


@mentor_learner_bp.route("/mentee", methods=["GET"])
@jwt_required()
def get_mentor_request():
    profile = resolve_profile(get_jwt_identity())
    if not profile:
        return jsonify({"error": "Profile not found"}), 404

    rows = get_startmentorship_request(profile.id)
    if not rows:
        return jsonify([]), 200
    return jsonify([row.to_dict() for row in rows]), 200