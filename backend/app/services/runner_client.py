"""Talks to the code-runner service. Uses only the standard library.

Needs two environment variables on the Flask service:
    RUNNER_URL      e.g. http://127.0.0.1:5001
    RUNNER_API_KEY  the same value as in the runner's .env
"""
import json
import os
import urllib.error
import urllib.request

RUNNER_TIMEOUT_SECONDS = 45  # a cold Go run can take ~15s


class RunnerError(Exception):
    def __init__(self, message, status=502):
        super().__init__(message)
        self.message = message
        self.status = status


def run_code(user_id, lang, code, stdin=""):
    """Runs code in the sandbox and returns the runner's JSON:
    {stdout, stderr, exitCode, timedOut, truncated, durationMs}"""
    runner_url = os.environ.get("RUNNER_URL")
    api_key = os.environ.get("RUNNER_API_KEY")
    if not runner_url or not api_key:
        raise RunnerError("Code runner is not configured", 503)

    payload = json.dumps(
        {"userId": str(user_id), "lang": lang, "code": code, "stdin": stdin}
    ).encode("utf-8")
    req = urllib.request.Request(
        runner_url.rstrip("/") + "/run",
        data=payload,
        headers={"Content-Type": "application/json", "x-api-key": api_key},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=RUNNER_TIMEOUT_SECONDS) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as err:
        # The runner answered but refused: busy, rate limited, too large...
        try:
            message = json.load(err).get("error", "Runner error")
        except Exception:
            message = "Runner error"
        raise RunnerError(message, err.code if err.code in (413, 429, 503) else 502)
    except (urllib.error.URLError, TimeoutError, OSError):
        raise RunnerError("Code runner is unavailable", 502)
