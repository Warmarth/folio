# Folio API

A Flask REST API for creating and managing profile cards. Profile details are stored in a local SQLite database, with optional profile images.

## Project structure

```text
folio/
├── app/
│   ├── __init__.py       # Flask application factory
│   ├── database.py       # SQLAlchemy instance
│   ├── models.py         # ProfileCard model
│   └── routes.py         # API routes
├── instance/             # Local SQLite database
├── run.py                # Development server entry point
└── requirements.txt
```

## Setup

1. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   pip install Flask-SQLAlchemy
   ```

3. Run the development server:

   ```powershell
   python run.py
   ```

The API is available at `http://127.0.0.1:5000/api`.

## Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/` | API welcome response |
| `POST` | `/api/create_profile` | Create a profile card |
| `GET` | `/api/all_profile` | List profile cards |
| `GET` | `/api/all_profile/<id>` | Get one profile card |
| `PUT` / `PATCH` | `/api/all_profile/<id>` | Update a profile card |
| `DELETE` | `/api/all_profile/<id>` | Delete a profile card |

The list endpoint accepts optional `page` and `per_page` query parameters. `per_page` is capped at 50.

## Create a profile

Send JSON or `multipart/form-data` to `POST /api/create_profile`.

```json
{
  "name": "Ada Lovelace",
  "email": "ada@example.com",
  "bio": "Mathematician and programmer"
}
```

For an image, use an `image` file field with multipart form data. Images must be image MIME types and no larger than 2 MB.

## Frontend

No frontend is included yet. A separate client application can live in a `frontend/` directory at the project root and consume this API.
