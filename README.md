# Folio

Folio is a full-stack developer-learning platform for working through exercises, tracking a profile, and receiving AI-assisted feedback on submissions.

## Projects

| Project | Stack | Documentation |
| --- | --- | --- |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS | [frontend README](frontend/my-app/README.md) |
| API | Flask, SQLAlchemy, SQLite, JWT, Groq | [backend README](backend/README.md) |

## Start the full application

1. Start the API from `backend` and configure its `.env` file as described in the [API README](backend/README.md).
2. Create `frontend/my-app/.env.local` with:

   ```env
   NEXT_PUBLIC_API_URL=http://127.0.0.1:5000
   ```

3. Start the frontend from `frontend/my-app` with `npm install` and `npm run dev`.

The API runs at `http://127.0.0.1:5000` and the web app runs at `http://localhost:3000`.
