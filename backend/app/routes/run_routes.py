"""POST /playground/run: checks the login, then asks the runner service to execute the code.

Needs two environment variables on the Flask service: RUNNER_URL and RUNNER_API_KEY
(see services/runner_client.py). Uses only the standard library.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.runner_client import run_code, RunnerError

run_bp = Blueprint("run", __name__, url_prefix="/playground")

LANGUAGES = {"go", "python", "javascript", "typescript"}
MAX_CODE_CHARS = 50_000
MAX_STDIN_CHARS = 10_000


@run_bp.post("/run")
@jwt_required()
def run_code_route():
    data = request.get_json(silent=True) or {}
    lang = data.get("lang")
    code = data.get("code")
    stdin = data.get("stdin", "")

    if lang not in LANGUAGES:
        return jsonify({"error": "Unsupported language"}), 400
    if not isinstance(code, str) or not code.strip():
        return jsonify({"error": "Write some code first"}), 400
    if len(code) > MAX_CODE_CHARS:
        return jsonify({"error": "Code is too large"}), 413
    if not isinstance(stdin, str) or len(stdin) > MAX_STDIN_CHARS:
        return jsonify({"error": "Input is too large"}), 413

    try:
        return jsonify(run_code(str(get_jwt_identity()), lang, code, stdin)), 200
    except RunnerError as err:
        return jsonify({"error": err.message}), err.status
