"""Grades a code submission by running it against an exercise's test cases."""
import time

from app.services.runner_client import run_code, RunnerError

GRADING_DEADLINE_SECONDS = 50   # stay under the web server's request timeout
MAX_STORED_TEXT = 2000          # keep saved output small


class GraderUnavailableError(Exception):
    """The runner could not be reached or refused the request."""


def normalize(text):
    """Trailing spaces on each line and the final newline are ignored."""
    lines = (text or "").replace("\r\n", "\n").split("\n")
    return "\n".join(line.rstrip() for line in lines).rstrip("\n")


class CodeGrader:
    def grade(self, exercise, code, user_id):
        lang = exercise.language.value
        runner_user = f"g-{user_id}"   # separate from practice runs, so Run clicks don't use up grading
        started = time.monotonic()
        results = []
        skip_reason = None   # once set, the remaining tests are not run

        for test in exercise.test_cases:
            if skip_reason is None and time.monotonic() - started > GRADING_DEADLINE_SECONDS:
                skip_reason = "Skipped: grading time limit reached"
            if skip_reason:
                results.append({
                    "test_id": test.id, "passed": False, "is_hidden": test.is_hidden,
                    "actual_output": "", "stderr": skip_reason,
                    "exit_code": None, "timed_out": False, "duration_ms": 0,
                })
                continue

            try:
                run = run_code(runner_user, lang, code, test.stdin)
            except RunnerError as err:
                raise GraderUnavailableError(err.message) from err

            actual = run.get("stdout") or ""
            passed = (
                run.get("exitCode") == 0
                and not run.get("timedOut")
                and not run.get("truncated")
                and normalize(actual) == normalize(test.expected_output)
            )
            if run.get("timedOut"):
                # An infinite loop will usually hang on every test; don't wait for each one.
                skip_reason = "Skipped: an earlier test timed out"
            results.append({
                "test_id": test.id,
                "passed": passed,
                "is_hidden": test.is_hidden,
                "actual_output": actual[:MAX_STORED_TEXT],
                "stderr": (run.get("stderr") or "")[:MAX_STORED_TEXT],
                "exit_code": run.get("exitCode"),
                "timed_out": bool(run.get("timedOut")),
                "duration_ms": run.get("durationMs"),
            })

        passed_count = sum(1 for r in results if r["passed"])
        total = len(results)
        return {
            "passed": total > 0 and passed_count == total,
            "results": results,
            "feedback": f"Passed {passed_count} of {total} tests.",
        }