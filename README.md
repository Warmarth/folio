# Folio

Folio is a Flask API for a developer-learning platform. It supports learner and mentor profiles, mentor and learner relationships, coding exercises, and AI-assisted evaluation of exercise submissions.

## Features

- Account registration and login with JWT authentication.
- Learner and mentor profiles, with optional profile image uploads.
- Exercise creation and browsing, including mentor-created exercises.
- Exercise submissions evaluated with Groq, with experience points awarded for successful work.
- Mentor requests and relationship management.
- SQLite storage for local development; optional Cloudflare R2 storage for uploaded images.

## Requirements

- Python 3.13 or later
- A Groq API key for AI exercise evaluation
- Cloudflare R2 credentials only if you use remote image uploads

## Configure

From the repository root, create `backend/.env`:

```env
SECRET_KEY=replace-with-a-long-random-secret
JWT_SECRET_KEY=replace-with-a-different-long-random-secret
GROQ_API_KEY=your-groq-api-key

# Optional: required for Cloudflare R2 image uploads
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET_NAME=your-bucket
R2_PUBLIC_URL=https://your-public-bucket-url
```

The local SQLite database is created at `backend/instance/app.db` when the API starts. Keep `.env` private and use distinct random values for the secret keys.

## Run locally

In PowerShell, from the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

The API listens at `http://127.0.0.1:5000`. Its root endpoint, `GET /api/`, returns a welcome response.

## Run with Docker

From `backend/`:

```powershell
docker compose up --build
```

Docker Compose reads `backend/.env` and persists SQLite data in `backend/instance/`.

## Authentication

Register or log in to receive a JWT:

```http
POST /auth/register
Content-Type: application/json

{"email":"ada@example.com","password":"a-strong-password"}
```

```http
POST /auth/login
Content-Type: application/json

{"email":"ada@example.com","password":"a-strong-password"}
```

Include the returned token on protected endpoints:

```http
Authorization: Bearer <access_token>
```

## Main API routes

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/auth/register` | Register an account |
| `POST` | `/auth/login` | Log in and receive a token |
| `GET` | `/api/` | API welcome response |
| `POST` | `/api/create_profile` | Create the current user's learner profile |
| `POST` | `/api/mentors_create_profile` | Create the current user's mentor profile |
| `GET` | `/api/profile` | Get the current user's profile |
| `GET` | `/api/all_profile` | List learner profiles |
| `GET` | `/api/all_mentors` | List mentor profiles |
| `POST` | `/api/exercises/create_exercise` | Create an exercise |
| `GET` | `/api/exercises/all_exercise` | List exercises |
| `POST` | `/api/submit/post_exercise/<exercise_id>` | Submit an exercise answer |
| `GET` | `/api/submit/submitted_exercise/<exercise_id>` | Get a submission |
| `POST` | `/api/mentor/<mentor_user_id>/request` | Request a mentor relationship |
| `PATCH` | `/api/mentor/<learner_id>/accept` | Accept a mentor request |
| `PATCH` | `/api/mentor/<learner_id>/decline` | Decline a mentor request |

Protected endpoints require a JWT. Profile and exercise lists support `page` and `per_page` query parameters; the maximum page size is 50.

## Exercise submission

Create an exercise with a title, description, and difficulty level:

```json
{
  "title": "Build a Flask route",
  "description": "Create a route that returns JSON.",
  "level": "easy"
}
```

Submit an answer as JSON:

```json
{"answer":"My solution and explanation."}
```

AI evaluation requires `GROQ_API_KEY`. The API awards experience points based on exercise difficulty when a submission is successful.
