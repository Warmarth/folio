# repositories/submit_exercise_repository.py
from app.models import Submit_Exercise,SubmissionStatusEnum
from app.database import db

class SubmitExerciseRepository:

    @staticmethod
    def get_completed(user_id, exercise_id):
        return Submit_Exercise.query.filter_by(user_id=user_id, exercise_id=exercise_id, is_completed=True).first()

    @staticmethod
    def get_in_progress(user_id, exercise_id):
        return Submit_Exercise.query.filter_by(
            user_id=user_id, exercise_id=exercise_id, is_completed=False
        ).first()

    @staticmethod
    def create(user_id, exercise_id, answer):
        submission = Submit_Exercise(
            user_id=user_id,
            exercise_id=exercise_id,
            answer=answer,
            status=SubmissionStatusEnum.evaluating,
        )
        db.session.add(submission)
        return submission

    @staticmethod
    def save():
        db.session.commit()