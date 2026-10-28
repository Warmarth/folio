"""Creates the exercises in exercises-seed.json through your API, as a mentor.

Usage (from this folder, any Python 3, nothing to install):
    python seed_exercises.py <API_URL> <ACCESS_TOKEN>

    API_URL       e.g. http://127.0.0.1:5000
    ACCESS_TOKEN  log in to Folio as a mentor, open the browser dev tools
                  (F12 > Application > Local Storage) and copy "access_token"
"""
import json
import sys
import urllib.error
import urllib.request

if len(sys.argv) != 3:
    sys.exit(__doc__)

api_url, token = sys.argv[1].rstrip("/"), sys.argv[2]

with open("exercises-seed.json", encoding="utf-8") as f:
    exercises = json.load(f)

for exercise in exercises:
    req = urllib.request.Request(
        f"{api_url}/api/exercises/create_exercise",
        data=json.dumps(exercise).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"created  {exercise['title']}  ({resp.status})")
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "replace")[:200]
        print(f"FAILED   {exercise['title']}  ({err.code}) {detail}")
    except urllib.error.URLError as err:
        sys.exit(f"Could not reach {api_url}: {err.reason}")
