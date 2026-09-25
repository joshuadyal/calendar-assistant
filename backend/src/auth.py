import os
import secrets
from dataclasses import dataclass

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.oauth2 import id_token

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.freebusy",
    "https://www.googleapis.com/auth/calendar.events",
]


@dataclass
class AuthenticatedUser:
    user_id: str
    email: str
    credentials: Credentials


class GoogleOAuth:
    def __init__(self) -> None:
        self.client_secrets_file = os.getenv(
            "GOOGLE_CLIENT_SECRETS_FILE", "credentials.json"
        )
        self.redirect_uri = os.getenv(
            "GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback"
        )

    def _flow(self, state: str | None = None, code_verifier: str | None = None) -> Flow:
        flow = Flow.from_client_secrets_file(
            self.client_secrets_file,
            scopes=SCOPES,
            state=state,
            code_verifier=code_verifier,
        )
        flow.redirect_uri = self.redirect_uri
        return flow

    def authorization_url(self) -> tuple[str, str, str | None]:
        state = secrets.token_urlsafe(32)
        flow = self._flow(state)
        url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        return url, state, flow.code_verifier

    def exchange_code(
        self, code: str, state: str, code_verifier: str | None = None
    ) -> AuthenticatedUser:
        flow = self._flow(state, code_verifier)
        flow.fetch_token(code=code)
        credentials = flow.credentials

        if not credentials.id_token:
            raise ValueError("Google did not return an identity token.")

        profile = id_token.verify_oauth2_token(
            credentials.id_token,
            Request(),
            audience=credentials.client_id,
        )
        user_id = profile["sub"]
        return AuthenticatedUser(
            user_id=user_id,
            email=profile.get("email", user_id),
            credentials=credentials,
        )

    @staticmethod
    def refresh_if_needed(user: AuthenticatedUser) -> AuthenticatedUser:
        credentials = user.credentials
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        return user


oauth = GoogleOAuth()


def calendar_auth():
    """Legacy CLI authentication; the HTTP API uses GoogleOAuth instead."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow

            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
    return creds
