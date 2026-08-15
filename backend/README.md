# Folio API

Folio is a Flask REST API for profile cards and learning exercises. It uses a local SQLite database and supports optional profile images.

## Features

- Create, view, update, and delete profile cards.
- Upload profile images with multipart form data.
- Create and manage exercises associated with a profile.
- Assign XP automatically from an exercise difficulty level.
- Run locally or with Docker Compose.

## Project structure

```text
backend/
├── app/
│   ├── __init__.py                 # Flask application factory and blueprint registration
│   ├── database.py                 # SQLAlchemy instance
│   ├── models.py                   # ProfileCard, Exercise, and ExerciseProgress models
│   └── routes/
│       ├── routes.py               # Profile-card API routes
│       └── exercise_route.py       # Exercise API routes
├── instance/                       # Local SQLite database location
├── compose.yaml                    # Docker Compose configuration
├── Dockerfile
├── requirements.txt
└── run.py                          # Development server entry point
```

## Run locally

From the `backend` directory:

1. Create and activate a virtual environment.

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install the dependencies.

   ```powershell
   pip install -r requirements.txt
   ```

3. Start the development server.

   ```powershell
   python run.py
   ```

The API is available at `http://127.0.0.1:5000/api`. Database tables are created automatically on startup.

## Run with Docker

From the `backend` directory:

```powershell
docker compose up --build
```

The API is then available at `http://127.0.0.1:5000/api`. The `instance` directory is mounted into the container so the SQLite database persists locally.

## API endpoints

### Profiles

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/` | Welcome response |
| `POST` | `/api/create_profile` | Create a profile card |
| `GET` | `/api/all_profile` | List profile cards |
| `GET` | `/api/all_profile/<profile_id>` | Get one profile card |
| `PUT`, `PATCH` | `/api/all_profile/<profile_id>` | Update a profile card |
| `DELETE` | `/api/all_profile/<profile_id>` | Delete a profile card |

The profile list supports `page` and `per_page` query parameters; `per_page` is limited to 50.

### Exercises

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/exercises/<profile_id>/create_exercise` | Create an exercise for a profile |
| `GET` | `/api/exercises/all_exercise` | List exercises |
| `GET` | `/api/exercises/all_exercise/<exercise_id>` | Get one exercise |
| `PUT`, `PATCH` | `/api/exercises/<profile_id>/all_exercise/<exercise_id>/update` | Update an exercise created by the profile |
| `DELETE` | `/api/exercises/<profile_id>/all_exercise/<exercise_id>/delete` | Delete an exercise created by the profile |

Exercises use one of these levels. The API assigns the matching XP value when an exercise is created or its level is updated.

| Level | XP |
| --- | ---: |
| `easy` | 2 |
| `medium` | 3 |
| `hard` | 5 |
| `expert` | 7 |
| `possible` | 9 |

## Request examples

Create a profile:

```json
POST /api/create_profile
{
  "name": "Ada Lovelace",
  "email": "ada@example.com",
  "bio": "Mathematician and programmer"
}
```

To include a profile image, submit `multipart/form-data` with an `image` file field. Image uploads must have an `image/*` MIME type and be at most 2 MB.

Create an exercise for an existing profile:

```json
POST /api/exercises/<profile_id>/create_exercise
{
  "title": "Build a Flask route",
  "description": "Create a route that returns JSON.",
  "level": "easy"
}
```

## Frontend

No frontend is included yet. A separate client can live in a `frontend/` directory at the repository root and consume this API.
