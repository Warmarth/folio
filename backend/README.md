# Folio API

Folio is a Flask REST API for a learning community. Users can register, create a profile, publish exercises, and submit answers for AI-assisted evaluation. The application uses SQLite for local persistence, JWTs for protected endpoints, and the Gemini API to evaluate exercise submissions.

## What is implemented

- User registration and login with bcrypt password hashing.
- JWT-protected profile creation, viewing, editing, and deletion.
- Optional profile-image uploads (up to 2 MB).
- Exercise creation and management by the user who created each exercise.
- Automatic XP assignment based on exercise difficulty.
- AI-assisted exercise submissions, with completion and score saved to the database.
- Pagination for profile and exercise listings.
- Local development and Docker Compose support.

## Project structure

```text
backend/
├── app/
│   ├── auth/routes.py              # Registration and login endpoints
│   ├── eveluator/ai_evaluator.py   # Gemini submission evaluator
│   ├── routes/
│   │   ├── routes.py               # Profile endpoints
│   │   ├── exercise_route.py       # Exercise endpoints
│   │   └── submitted.py            # Submission endpoint
│   ├── __init__.py                 # Application factory and blueprints
│   ├── database.py                 # SQLAlchemy setup
│   └── models.py                   # Database models
├── instance/                       # SQLite database location
├── compose.yaml                    # Docker Compose configuration
├── Dockerfile
├── requirements.txt
└── run.py                          # Development server entry point
```

## Requirements

- Python 3.13 (the Docker image uses Python 3.13)
- A Gemini API key for exercise evaluation

Create `backend/.env` with these values before starting the API:

```env
SECRET_KEY=replace-with-a-long-random-secret
JWT_SECRET_KEY=replace-with-a-different-long-random-secret
GEMINI_API_KEY=your-gemini-api-key
```

`GEMINI_API_KEY` is required when using the submission endpoint. Tables are created automatically when the application starts.

## Run locally

From the `backend` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

The API listens at `http://127.0.0.1:5000`. API routes are available under `/api`, except the authentication routes, which are under `/auth`.

## Run with Docker

From the `backend` directory:

```powershell
docker compose up --build
```

Docker loads variables from `.env` and mounts `instance/` so the SQLite database persists on the host.

## Authentication

Register a user, then log in to receive an access token:

```http
POST /auth/register
Content-Type: application/json

{
  "email": "ada@example.com",
  "password": "a-strong-password"
}
```

```http
POST /auth/login
Content-Type: application/json

{
  "email": "ada@example.com",
  "password": "a-strong-password"
}
```

For protected endpoints, send the token returned by login:

```http
Authorization: Bearer <access_token>
```

## Endpoints

### General and profiles

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/` | No | Welcome response |
| `POST` | `/api/create_profile` | Yes | Create the current user's profile |
| `GET` | `/api/profile` | Yes | Get the current user's profile |
| `GET` | `/api/all_profile` | No | List profiles |
| `PUT`, `PATCH` | `/api/edit_profile` | Yes | Update the current user's profile |
| `DELETE` | `/api/delete_user` | Yes | Delete the current user's profile |

Profiles accept `name` and optional `bio`. To include an image, send `multipart/form-data` with an `image` file field. The image must have an `image/*` MIME type and be no larger than 2 MB.

### Exercises

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/api/exercises/create_exercise` | Yes | Create an exercise |
| `GET` | `/api/exercises/all_exercise` | Yes | List exercises |
| `GET` | `/api/exercises/all_exercise/<exercise_id>` | Yes | Get an exercise |
| `PUT`, `PATCH` | `/api/exercises/all_exercise/<exercise_id>/update` | Yes | Update your exercise |
| `DELETE` | `/api/exercises/all_exercise/<exercise_id>/delete` | Yes | Delete your exercise |

Creating an exercise requires that the current user already has a profile. Exercise requests use JSON:

```json
{
  "title": "Build a Flask route",
  "description": "Create a route that returns JSON.",
  "level": "easy"
}
```

| Level | XP |
| --- | ---: |
| `easy` | 2 |
| `medium` | 3 |
| `hard` | 5 |
| `expert` | 7 |
| `possible` | 9 |

Both listing endpoints accept optional `page` and `per_page` query parameters. `per_page` is capped at 50.

### Submissions

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/api/submit/post_exercise/<exercise_id>` | Yes | Submit an answer for AI evaluation |

Submit a JSON request:

```json
{
  "answer": "My solution and explanation."
}
```

The evaluator compares the answer with the exercise prompt. A completed submission receives the exercise's XP value as its score; an unsuccessful one receives `0`. Once a user has completed an exercise, further submissions for that exercise are rejected.

## Current scope

This repository currently contains the API only; a frontend has not yet been added. The local SQLite database is intended for development. Use managed configuration and a production database before deploying the service.
