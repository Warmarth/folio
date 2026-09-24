from app.repository.exercise_submission import SubmitExerciseRepository
from app.models import SubmissionStatusEnum,Profile,Exercise,User
from app.evaluator.ai_evaluator import evaluator_ai
from datetime import datetime,timezone


class DuplicateSubmissionError(Exception): pass
class ProfileRequiredError(Exception): pass
class EvaluationError(Exception):
    def __init__(self, submission):
        self.submission = submission

class SubmitExerciseService:

    def __init__(self, repo=SubmitExerciseRepository()):
        self.repo = repo

    def submit(self, user_id, exercise_id, answer):
        if not Profile.query.filter_by(user_id=user_id).first():
            raise ProfileRequiredError()

        exercise = Exercise.query.get_or_404(exercise_id)

        if self.repo.get_completed(user_id, exercise_id):
            raise DuplicateSubmissionError()

        submission = self.repo.get_in_progress(user_id, exercise_id)
        if submission:
            submission.answer = answer
            submission.status = SubmissionStatusEnum.evaluating
        else:
            submission = self.repo.create(user_id, exercise_id, answer)
        self.repo.save()

        question = {
            "title": exercise.title,
            "description": exercise.description,
            "answer": answer,
        }

        try:
            result = evaluator_ai(param=question)
        except Exception:
            submission.status = SubmissionStatusEnum.failed
            self.repo.save()
            raise EvaluationError(submission)

        self._apply_result(submission, user_id, exercise.xp_points, result)
        self.repo.save()
        return submission

    def _apply_result(self, submission, user_id, xp_points, result):
        is_completed = result["passed"]
        submission.status = SubmissionStatusEnum.completed
        submission.score = xp_points if is_completed else 0
        submission.feedback = result["feedback"]
        submission.is_completed = is_completed
        submission.completed_at = datetime.now(timezone.utc)

        if is_completed:
            user = User.query.get(user_id)
            user.total_xp = (user.total_xp or 0) + submission.score