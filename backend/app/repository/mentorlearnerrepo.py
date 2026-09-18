from app.models import MentorLearner,MentorLearnerStatusEnum
from app.database import db
from datetime import datetime,timezone


def find_by_pair(mentor_id:str,learner_id:str):
    """return a single row from mentorlearner table or none"""
    return MentorLearner.query.filter_by(mentor_id=mentor_id,learner_id=learner_id).first()



def create(mentor_id:str,learner_id:str):
    """insert new row all starting at pending"""
    row = MentorLearner(
        mentor_id=mentor_id,
        learner_id=learner_id,
        status=MentorLearnerStatusEnum.pending,
        requested_at=datetime.now(timezone.utc)
    )
    
    db.session.add(row)
    db.session.commit()
    return row

def update_status(row:MentorLearner,new_status:MentorLearnerStatusEnum):
    """Flip an existing row to a new status and stamp the matching timestamp."""
    row.status = new_status
    
    if new_status == MentorLearnerStatusEnum.pending:
        row.requested_at = datetime.now(timezone.utc)
        row.responded_at = None
        row.ended_at = None
    elif new_status in (MentorLearnerStatusEnum.active,MentorLearnerStatusEnum.declined):
        row.responded_at = datetime.now(timezone.utc)
    elif new_status == MentorLearnerStatusEnum.ended:
        row.ended_at = datetime.now(timezone.utc)
    
    db.session.commit()
    return row

def get_mentee(mentor_id: str):
    """Get all mentorship requests/relationships for a given mentor (by profile ID)."""
    return MentorLearner.query.filter_by(mentor_id=mentor_id).order_by(
        MentorLearner.requested_at.desc()
    ).all()