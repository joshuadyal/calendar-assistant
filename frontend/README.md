# Daymark

The frontend for the Calendar Assistant. It provides Google sign-in, a calendar workspace, chat with the agent, approval controls for calendar changes, and a recent activity view.

## Getting Started

The backend should be running at `http://localhost:8000` with the CORS and OAuth settings described in `backend/README.md`.

Optional: create `.env.local` to point the frontend at another backend:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Run the development server from this directory:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) to use the app. The first screen checks `/auth/me`; unauthenticated users are sent through the backend Google login flow.

The calendar month view is intentionally honest about the current backend contract: event listing is not exposed yet, so connected event data appears through assistant conversations until a calendar-read endpoint is added.

## Validation

```bash
npm run lint
npm run build
```
