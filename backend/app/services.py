from app.models import MentorLearnerStatusEnum
from app.repository import mentorlearnerrepo as repo


class MentorLearnerError(Exception):
    """Raised when a requested transition doesn't make sense for the row's current status."""
    pass


def request_mentor(mentor_id: str, learner_id: str):
    """Learner requests a mentor. Reuses the row if one already exists for
    this pair (e.g. after a decline or an ended relationship) instead of
    creating a duplicate."""
    row = repo.find_by_pair(mentor_id, learner_id)

    if row is None:
        return repo.create(mentor_id, learner_id)

    return repo.update_status(row, MentorLearnerStatusEnum.pending)


def accept_request(mentor_id: str, learner_id: str):
    row = repo.find_by_pair(mentor_id, learner_id)
    if row is None:
        raise MentorLearnerError("No relationship found for this mentor/learner pair.")
    if row.status != MentorLearnerStatusEnum.pending:
        raise MentorLearnerError(f"Cannot accept a relationship in '{row.status.value}' status.")

    return repo.update_status(row, MentorLearnerStatusEnum.active)


def decline_request(mentor_id: str, learner_id: str):
    row = repo.find_by_pair(mentor_id, learner_id)
    if row is None:
        raise MentorLearnerError("No relationship found for this mentor/learner pair.")
    if row.status != MentorLearnerStatusEnum.pending:
        raise MentorLearnerError(f"Cannot decline a relationship in '{row.status.value}' status.")

    return repo.update_status(row, MentorLearnerStatusEnum.declined)


def end_relationship(caller_id: str, other_user_id: str):
    """Either the mentor or the learner can end an active relationship.
    caller_id is whoever is logged in and calling this; other_user_id is
    the id in the URL. We don't know upfront which of them is the mentor
    and which is the learner, so we check both directions."""
    row = repo.find_by_pair(caller_id, other_user_id)  # caller as mentor
    if row is None:
        row = repo.find_by_pair(other_user_id, caller_id)  # caller as learner

    if row is None:
        raise MentorLearnerError("No relationship found between these two users.")
    if row.status != MentorLearnerStatusEnum.active:
        raise MentorLearnerError(f"Cannot end a relationship in '{row.status.value}' status.")

    return repo.update_status(row, MentorLearnerStatusEnum.ended)

def get_relationship_status(mentor_id: str, learner_id: str):
    """Returns the row if one exists for this pair, or None if the learner
    has never requested this mentor. The route decides how to represent
    'no relationship yet' vs an actual status."""
    return repo.find_by_pair(mentor_id, learner_id)

def get_startmentorship_request(mentor_id:str):
    """Return all user that has sent a mentorship request"""
    return repo.get_mentee(mentor_id=mentor_id)