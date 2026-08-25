# Folio frontend

The Folio web client is a [Next.js](https://nextjs.org/) 16 application for a practical developer-learning platform. It provides the landing page, account registration and sign-in, profiles, exercise browsing, and exercise submission views.

It connects to the Flask API in [`../../backend`](../../backend).

## Requirements

- Node.js 20.9 or later
- npm
- A running Folio API (by default, at `http://127.0.0.1:5000`)

## Configuration

Create a `.env.local` file in this directory:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:5000
```

`NEXT_PUBLIC_API_URL` is exposed to the browser and must point to the API URL. The backend's CORS configuration permits `http://localhost:3000` and `http://127.0.0.1:3000` during local development.

## Run locally

```powershell
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

Other commands:

```powershell
npm run lint
npm run build
npm run start
```

## Application routes

| Route | Purpose |
| --- | --- |
| `/` | Product landing page |
| `/register` | Create an account through the API |
| `/login` | Sign in and store the JWT in browser local storage |
| `/me` | View and manage the signed-in profile |
| `/dashboard` | View profiles |
| `/dashboard/exercises` | Browse available exercises |
| `/dashboard/exercises/[id]` | View and submit an exercise answer |

Authenticated API calls use the access token stored as `access_token` in local storage. Start the backend and create an account before trying protected dashboard features.

## Technology

- Next.js 16 and React 19
- TypeScript
- Tailwind CSS 4
- ESLint
