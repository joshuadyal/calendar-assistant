# Calendar Assistant API

A FastAPI backend for an AI calendar assistant. The agent uses OpenAI and Google Calendar through LangChain and LangGraph. A separate frontend can use the HTTP API to sign users into Google, send chat messages, continue conversations, and approve calendar changes.

## Features

- View calendar events and individual event details
- Check busy periods and availability
- Create, update, and delete Google Calendar events
- Sign users in with Google OAuth from the frontend
- Keep Google Calendar credentials isolated per signed-in account
- Preserve conversation state with a `thread_id`
- Require explicit approval before calendar-changing actions
- Expose interactive API documentation through FastAPI

## Requirements

- Python 3.12 or newer
- A Google Cloud project with the Google Calendar API enabled
- An OAuth client credentials file named `credentials.json`
- An OpenAI API key

The project currently uses an in-project virtual environment at `venv/`.

## Setup

1. Create or activate the virtual environment.

   ```powershell
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

2. Install dependencies.

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Create a **Web application** OAuth client in Google Cloud Console. Add this authorized redirect URI:

```text
http://localhost:8000/auth/google/callback
```

Download the client JSON as `credentials.json` in the project root. The backend, rather than the frontend, exchanges the authorization code so the client secret is never sent to the browser.

4. Create a `.env` file in the project root.

   ```text
   OPENAI_API_KEY=your-openai-api-key
   SESSION_SECRET=replace-with-a-long-random-secret
   FRONTEND_URL=http://localhost:3000
   GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
   FRONTEND_ORIGINS=http://localhost:3000,http://localhost:5173
   ```

Set `COOKIE_SECURE=true` when serving the API over HTTPS. Keep `SESSION_SECRET` private and use a different value in each environment.

## Run The API

Run this command from the project root:

```powershell
venv\Scripts\python.exe -m uvicorn api:app --app-dir src --reload
```

The API is available at `http://127.0.0.1:8000`.

FastAPI documentation is available at:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## API Endpoints

### Health check

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

### Sign in with Google

```http
GET /auth/google/login
```

The frontend should navigate the browser to this endpoint. The backend redirects to Google, validates the callback, creates a signed session cookie, and redirects to:

```text
{FRONTEND_URL}/auth/callback?google_auth=success
```

On failure it redirects with `google_auth=error` and an `error` query parameter. The frontend should then call `GET /auth/me` to retrieve the signed-in email.

### Current account

```http
GET /auth/me
```

Response when signed in:

```json
{
  "authenticated": true,
  "email": "user@example.com"
}
```

Response when signed out:

```json
{
  "authenticated": false,
  "email": null
}
```

### Sign out

```http
POST /auth/logout
```

The frontend must include cookies on API requests. For `fetch`, use `credentials: "include"`.

### Send a chat message

```http
POST /chat
Content-Type: application/json
```

Request:

```json
{
  "message": "What meetings do I have tomorrow?"
}
```

This endpoint requires a signed-in Google session. For a new conversation, omit `thread_id`. The response provides one. Send that same ID on later messages to continue the conversation. Threads are bound to the account that created them.

```json
{
  "message": "What about Friday?",
  "thread_id": "0192f2a8-7f1a-7c5d-b9d7-123456789abc"
}
```

Response:

```json
{
  "thread_id": "0192f2a8-7f1a-7c5d-b9d7-123456789abc",
  "status": "success",
  "message": "You have ...",
  "events_affected": [],
  "pending_action": null
}
```

Possible `status` values are `success`, `needs_approval`, `cancelled`, and `error`.

### Approve or reject a calendar change

Creating, updating, or deleting an event returns a response with `status` set to `needs_approval`. The frontend should display the approval prompt and send the same `thread_id` to:

```http
POST /chat/{thread_id}/approval
Content-Type: application/json
```

Approve the action:

```json
{
  "decision": "approve"
}
```

Reject the action:

```json
{
  "decision": "reject"
}
```

An approval request for a thread without a pending action returns HTTP `409`. Unexpected processing failures return HTTP `500`.

## Frontend Integration Flow

1. Send the user's message to `POST /chat`.
2. Store the returned `thread_id` for the conversation.
3. If the response status is `needs_approval`, show the pending action to the user.
4. Post `approve` or `reject` to `/chat/{thread_id}/approval`.
5. Render the returned message and continue using the same `thread_id`.

The API permits requests from the origins listed in `FRONTEND_ORIGINS`. Set this variable to the exact origin or comma-separated origins used by the frontend.

## Project Structure

```text
src/
  api.py                FastAPI application and HTTP schemas
  main.py               Agent tools, model configuration, and CLI runner
  auth.py               Google Calendar OAuth flow
  calendar_service.py   Google Calendar API operations
  definitions.py        Pydantic agent response models
  guardrails.py         Prompt-injection input guardrail
  helpers.py            Date and time parsing helpers
  logger.py             File logging configuration
```

## Security Notes

- Keep `.env`, `credentials.json`, and `token.json` out of version control. The web API does not use `token.json`; it stores OAuth credentials in process memory for the current server run.
- Do not expose the API publicly without adding authentication and HTTPS.
- The current session and LangGraph checkpointer are in-memory. Google sign-ins and conversation state are lost when the API process restarts. Use a persistent session/token store and durable LangGraph checkpointer before deploying multiple workers or production workloads.
- Calendar-changing tools are protected by the agent's human-in-the-loop approval interrupt.

## Validation

Compile the Python source files:

```powershell
venv\Scripts\python.exe -m py_compile src\main.py src\api.py
```

The health endpoint can be checked at `GET /health` after starting the server.
