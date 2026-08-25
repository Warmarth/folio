# Folio API

The Folio API is a Flask application for a practical developer-learning platform. It handles account authentication, learner profiles, exercises, and AI-assisted exercise submissions. The companion Next.js application lives in [`../frontend/my-app`](../frontend/my-app).

## Features

- Registration and login with bcrypt password hashing and JWT access tokens.
- Create, view, update, and delete learner profiles, including optional image uploads.
- Create, list, view, update, and delete exercises.
- Difficulty-based XP for exercises.
- AI-assisted submission evaluation with Groq.
- SQLite persistence for local development.

## Requirements

- Python 3.13 or later
- A Groq API key for exercise evaluation

## Configuration

Create `backend/.env`:

```env
SECRET_KEY=replace-with-a-long-random-secret
JWT_SECRET_KEY=replace-with-a-different-long-random-secret
GROQ_API_KEY=your-groq-api-key
```

`GROQ_API_KEY` is needed only when submitting exercises for AI evaluation. SQLite tables are created automatically on startup and the development database is stored in `backend/instance/app.db`.

## Run locally

From this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

The server listens at `http://127.0.0.1:5000`. To use the frontend, set its `NEXT_PUBLIC_API_URL` to that address and run it on port 3000.

## Run with Docker

From this directory:

```powershell
docker compose up --build
```

Docker reads `.env` and mounts `instance/` so local SQLite data persists.

## Authentication

Register and log in to receive a token:

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

Send the returned token with protected requests:

```http
Authorization: Bearer <access_token>
```

## API endpoints

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | No | Register an account |
| `POST` | `/auth/login` | No | Log in and receive a JWT |
| `GET` | `/api/` | No | API welcome response |
| `POST` | `/api/create_profile` | Yes | Create the current user's profile |
| `GET` | `/api/profile` | Yes | Get the current user's profile |
| `GET` | `/api/all_profile` | Yes | List profiles |
| `GET` | `/api/all_profile/<profile_id>` | No | Get one profile |
| `PUT`, `PATCH` | `/api/edit_profile` | Yes | Update the current user's profile |
| `DELETE` | `/api/delete_user` | Yes | Delete the current user's profile |
| `POST` | `/api/exercises/create_exercise` | Yes | Create an exercise |
| `GET` | `/api/exercises/all_exercise` | Yes | List exercises |
| `GET` | `/api/exercises/all_exercise/<exercise_id>` | Yes | Get one exercise |
| `PUT`, `PATCH` | `/api/exercises/all_exercise/<exercise_id>/update` | Yes | Update an exercise you created |
| `DELETE` | `/api/exercises/all_exercise/<exercise_id>/delete` | Yes | Delete an exercise you created |
| `POST` | `/api/submit/post_exercise/<exercise_id>` | Yes | Submit an answer for evaluation |
| `GET` | `/api/submit/submitted_exrecise/<exercise_id>` | Yes | Get a completed submission |

Profile and exercise listings support `page` and `per_page` query parameters; `per_page` is capped at 50. Profile image uploads must be image files no larger than 2 MB.

## Exercise payloads

Create an exercise:

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

Submit an answer:

```json
{"answer":"My solution and explanation."}
```

Completed submissions receive the exercise XP; unsuccessful submissions receive `0`. A user cannot submit an exercise again after completing it.

## Project layout

```text
backend/
├── app/
│   ├── auth/              # Registration and login routes
│   ├── eveluator/         # Groq evaluation integration
│   ├── routes/            # Profile, exercise, and submission routes
│   ├── database.py        # SQLAlchemy setup
│   └── models.py          # Database models
├── instance/              # Local SQLite database
├── compose.yaml
├── Dockerfile
├── requirements.txt
└── run.py                 # Development server entry point
```
