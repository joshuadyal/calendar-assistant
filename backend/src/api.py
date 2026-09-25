import os
from threading import Lock
from typing import Any, Literal
from urllib.parse import urlencode

from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from langchain_core.runnables import Runnable
from langchain_core.utils.uuid import uuid7
from langgraph.types import Command
from pydantic import BaseModel, Field
from starlette.middleware.sessions import SessionMiddleware

from auth import AuthenticatedUser, oauth
from calendar_service import CalendarService
from definitions import CalendarAgentResponse
from logger import logger
from main import build_agent, request_calendar_service


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10_000)
    thread_id: str | None = None


class ApprovalRequest(BaseModel):
    decision: Literal["approve", "reject"]


class ChatResponse(BaseModel):
    thread_id: str
    status: Literal["success", "needs_approval", "cancelled", "error"]
    message: str
    events_affected: list[str] = Field(default_factory=list)
    pending_action: str | None = None


class AuthResponse(BaseModel):
    authenticated: bool
    email: str | None = None


class AgentRuntime:
    def __init__(self) -> None:
        self._agent: Runnable | None = None
        self._initialization_lock = Lock()
        self._calendar_services: dict[str, CalendarService] = {}
        self._thread_users: dict[str, str] = {}

    def _get_agent(self) -> Runnable:
        if self._agent is None:
            with self._initialization_lock:
                if self._agent is None:
                    self._agent = build_agent()
        return self._agent

    @staticmethod
    def _config(thread_id: str) -> dict[str, Any]:
        return {"configurable": {"thread_id": thread_id}}

    def _response(self, agent: Runnable, thread_id: str) -> ChatResponse:
        state = agent.get_state(self._config(thread_id))

        if state.interrupts:
            interrupt = state.interrupts[0].value
            review_configs = interrupt.get("review_configs", [])
            action_requests = interrupt.get("action_requests", [])
            action_name = (
                review_configs[0].get("action_name") if review_configs else None
            )
            return ChatResponse(
                thread_id=thread_id,
                status="needs_approval",
                message="Approval is required before changing your calendar.",
                pending_action=action_name
                or (action_requests[0].get("name") if action_requests else None),
            )

        structured = state.values.get("structured_response")
        if structured is None:
            return ChatResponse(
                thread_id=thread_id,
                status="error",
                message="The agent did not return a response.",
            )

        if isinstance(structured, CalendarAgentResponse):
            response = structured
        else:
            response = CalendarAgentResponse.model_validate(structured)

        return ChatResponse(
            thread_id=thread_id,
            status=response.status,
            message=response.message,
            events_affected=response.events_affected,
        )

    def _service_for(self, user: AuthenticatedUser) -> CalendarService:
        user = oauth.refresh_if_needed(user)
        with self._initialization_lock:
            if user.user_id not in self._calendar_services:
                self._calendar_services[user.user_id] = CalendarService(
                    user.credentials
                )
            return self._calendar_services[user.user_id]

    def chat(self, request: ChatRequest, user: AuthenticatedUser) -> ChatResponse:
        thread_id = request.thread_id or str(uuid7())
        owner = self._thread_users.get(thread_id)
        if owner is not None and owner != user.user_id:
            raise PermissionError("This conversation belongs to another account.")
        self._thread_users[thread_id] = user.user_id
        agent = self._get_agent()
        config = self._config(thread_id)

        logger.info("API request | thread=%s", thread_id)
        token = request_calendar_service.set(self._service_for(user))
        try:
            for _ in agent.stream_events(
                {"messages": [{"role": "user", "content": request.message}]},
                config=config,
                version="v3",
            ):
                pass
        finally:
            request_calendar_service.reset(token)

        return self._response(agent, thread_id)

    def approve(
        self,
        thread_id: str,
        decision: Literal["approve", "reject"],
        user: AuthenticatedUser,
    ) -> ChatResponse:
        if self._thread_users.get(thread_id) != user.user_id:
            raise PermissionError("This conversation belongs to another account.")
        agent = self._get_agent()
        config = self._config(thread_id)
        state = agent.get_state(config)
        if not state.interrupts:
            raise ValueError("No pending approval exists for this thread.")

        resume_value = {"decisions": [{"type": decision}]}
        logger.info("API approval | thread=%s | decision=%s", thread_id, decision)
        token = request_calendar_service.set(self._service_for(user))
        try:
            for _ in agent.stream_events(
                Command(resume=resume_value),
                config=config,
                version="v3",
            ):
                pass
        finally:
            request_calendar_service.reset(token)

        return self._response(agent, thread_id)


runtime = AgentRuntime()
app = FastAPI(title="Calendar Assistant API", version="1.0.0")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SESSION_SECRET", "change-this-in-production"),
    https_only=os.environ.get("COOKIE_SECURE", "false").lower() == "true",
    same_site="lax",
)

origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS", "http://localhost:3000,http://localhost:5173"
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def current_user(request: Request) -> AuthenticatedUser:
    user_id = request.session.get("user_id")
    user = users.get(user_id) if user_id else None
    if user is None:
        raise HTTPException(status_code=401, detail="Sign in with Google first.")
    return user


users: dict[str, AuthenticatedUser] = {}


@app.get("/auth/google/login")
def google_login(request: Request) -> RedirectResponse:
    url, state, code_verifier = oauth.authorization_url()
    request.session["oauth_state"] = state
    request.session["oauth_code_verifier"] = code_verifier
    return RedirectResponse(url)


@app.get("/auth/google/callback")
def google_callback(
    request: Request, code: str | None = None, state: str | None = None
):
    expected_state = request.session.pop("oauth_state", None)
    code_verifier = request.session.pop("oauth_code_verifier", None)
    if not code or not state or not expected_state or state != expected_state:
        return RedirectResponse(_frontend_redirect("error", "Invalid OAuth state."))
    try:
        user = oauth.exchange_code(code, state, code_verifier)
        users[user.user_id] = user
        request.session["user_id"] = user.user_id
        return RedirectResponse(_frontend_redirect("success"))
    except Exception:
        logger.exception("Google OAuth callback failed")
        return RedirectResponse(_frontend_redirect("error", "Google sign-in failed."))


@app.get("/auth/me", response_model=AuthResponse)
def auth_me(request: Request) -> AuthResponse:
    user_id = request.session.get("user_id")
    user = users.get(user_id) if user_id else None
    return AuthResponse(
        authenticated=user is not None, email=user.email if user else None
    )


@app.post("/auth/logout", response_model=AuthResponse)
def logout(request: Request) -> AuthResponse:
    request.session.clear()
    return AuthResponse(authenticated=False)


@app.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, request: Request) -> ChatResponse:
    try:
        user = current_user(request)
        return await run_in_threadpool(runtime.chat, body, user)
    except HTTPException:
        raise
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except Exception as error:
        logger.exception("API chat failed")
        raise HTTPException(
            status_code=500, detail="Unable to process the chat request."
        ) from error


@app.post("/chat/{thread_id}/approval", response_model=ChatResponse)
async def approve(
    thread_id: str, body: ApprovalRequest, request: Request
) -> ChatResponse:
    try:
        user = current_user(request)
        return await run_in_threadpool(runtime.approve, thread_id, body.decision, user)
    except HTTPException:
        raise
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except Exception as error:
        logger.exception("API approval failed | thread=%s", thread_id)
        raise HTTPException(
            status_code=500, detail="Unable to process the approval."
        ) from error


def _frontend_redirect(status: str, error: str | None = None) -> str:
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    params = {"google_auth": status}
    if error:
        params["error"] = error
    return f"{frontend_url}/auth/callback?{urlencode(params)}"
