from app.repository.exercise_submission import SubmitExerciseRepository
from app.models import SubmissionStatusEnum, Profile, Exercise, User
from app.evaluator.ai_evaluator import evaluator_ai, code_feedback_ai
from app.services.code_grader import CodeGrader, GraderUnavailableError
from app.database import db
import logging
import time
from datetime import datetime, timezone
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError


AI_FEEDBACK_BUDGET_SECONDS = 35   # skip the AI note if grading already took this long


class DuplicateSubmissionError(Exception): pass
class ProfileRequiredError(Exception): pass
class EvaluationError(Exception):
    def __init__(self, submission):
        self.submission = submission


class SubmitExerciseService:

    def __init__(self, repo=SubmitExerciseRepository(), grader=CodeGrader()):
        self.repo = repo
        self.grader = grader

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

        # Exercises with test cases are graded by running the code against them.
        if exercise.test_cases:
            started = time.monotonic()
            try:
                outcome = self.grader.grade(exercise, answer, user_id)
            except GraderUnavailableError:
                submission.status = SubmissionStatusEnum.failed
                self.repo.save()
                raise EvaluationError(submission)

            # The tests decide pass or fail; the AI only adds feedback. Skipped if grading
            # was already slow, to stay inside the web server's time limit.
            feedback = outcome["feedback"]
            if time.monotonic() - started < AI_FEEDBACK_BUDGET_SECONDS:
                ai_text = self._ai_feedback(exercise, answer, outcome)
                if ai_text:
                    feedback = f"{feedback}\n\n{ai_text}"

            self._finish(
                submission, user_id, exercise.xp_points,
                {"passed": outcome["passed"], "feedback": feedback},
                test_results=outcome["results"],
            )
            return submission

        # Everything else keeps the AI evaluator. The task text used to live in
        # `description`, so rebuild it from the separate fields to keep the AI's view the same.
        parts = [exercise.description, exercise.category, exercise.instructions, exercise.evaluation_criteria]
        question = {
            "title": exercise.title,
            "description": " ".join(p.strip() for p in parts if p and p.strip()),
            "answer": answer,
        }

        try:
            result = evaluator_ai(param=question)
        except Exception:
            submission.status = SubmissionStatusEnum.failed
            self.repo.save()
            raise EvaluationError(submission)

        self._finish(submission, user_id, exercise.xp_points, result)
        return submission

    def _ai_feedback(self, exercise, answer, outcome):
        """Short tutor-style feedback from the AI, or None if it fails (grading never depends on it)."""
        by_id = {t.id: t for t in exercise.test_cases}
        lines = []
        for i, r in enumerate(outcome["results"], start=1):
            test = by_id.get(r["test_id"])
            status = "passed" if r["passed"] else "failed"
            if r["is_hidden"] or test is None:
                lines.append(f"Test {i} (hidden): {status}")   # never reveal hidden inputs or outputs
                continue
            line = f"Test {i}: {status}"
            if not r["passed"]:
                line += (f" | input: {test.stdin[:200]!r} | expected: {test.expected_output[:200]!r}"
                         f" | got: {(r.get('actual_output') or '')[:200]!r}")
                if r.get("stderr"):
                    line += f" | error: {r['stderr'][:400]!r}"
                if r.get("timed_out"):
                    line += " | time limit reached"
            lines.append(line)

        try:
            return code_feedback_ai({
                "title": exercise.title,
                "language": exercise.language.value,
                "task": " ".join(p.strip() for p in (exercise.description, exercise.instructions) if p and p.strip()),
                "criteria": (exercise.evaluation_criteria or "").strip(),
                "code": answer,
                "passed": outcome["passed"],
                "tests": "\n".join(lines),
            })
        except Exception:
            logging.exception("AI feedback failed; keeping the plain test summary")
            return None

    def _finish(self, submission, user_id, xp_points, result, test_results=None):
        """Records the result and adds the XP, all in one commit.

        The database allows only one passed submission per user and exercise. If two
        requests pass at the same moment, the second one fails with an IntegrityError
        (it can surface at the XP update or at the commit). Everything is rolled back,
        so its XP is not added either, and it is reported as a duplicate."""
        try:
            self._apply_result(submission, user_id, xp_points, result)
            if test_results is not None:
                submission.test_results = test_results
            self.repo.save()
        except IntegrityError:
            db.session.rollback()
            raise DuplicateSubmissionError()

    def _apply_result(self, submission, user_id, xp_points, result):
        is_completed = result["passed"]
        submission.status = SubmissionStatusEnum.completed
        submission.score = xp_points if is_completed else 0
        submission.feedback = result["feedback"]
        submission.is_completed = is_completed
        submission.completed_at = datetime.now(timezone.utc)

        if is_completed:
            # Added by the database in one statement, so two submissions finishing at the
            # same time can't overwrite each other's XP (read, add, write would).
            User.query.filter_by(id=user_id).update(
                {User.total_xp: func.coalesce(User.total_xp, 0) + submission.score},
                synchronize_session=False,
            )