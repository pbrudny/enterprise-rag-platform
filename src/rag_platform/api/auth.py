"""HTTP Basic Auth gate for the deployed API/frontend.

Disabled by default (empty credentials, i.e. local dev) — only activates
when both settings are explicitly configured, so it never gets in the way
of local development and only matters for the deployed instance, which
makes real, billed LLM calls and would otherwise be open to anyone who
finds the URL.
"""

import base64
import binascii
import secrets

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from rag_platform.config import Settings


class BasicAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: Settings) -> None:
        super().__init__(app)
        # Keep the settings object itself, not a snapshot of its two fields
        # at construction time — the shared FastAPI app is a module-level
        # singleton built once, so reading fresh on every request is what
        # lets tests override credentials via monkeypatch/dependency
        # overrides without needing to reconstruct the app or middleware.
        self._settings = settings

    async def dispatch(self, request: Request, call_next):
        user = self._settings.basic_auth_user
        password = self._settings.basic_auth_password
        if not (user and password):
            return await call_next(request)

        if self._is_authorized(request, user, password):
            return await call_next(request)

        return Response(
            status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="rag-platform"'},
        )

    def _is_authorized(self, request: Request, user: str, password: str) -> bool:
        header = request.headers.get("authorization", "")
        if not header.lower().startswith("basic "):
            return False
        try:
            decoded = base64.b64decode(header[6:]).decode("utf-8")
            req_user, _, req_password = decoded.partition(":")
        except (ValueError, binascii.Error, UnicodeDecodeError):
            return False

        return secrets.compare_digest(req_user, user) and secrets.compare_digest(
            req_password, password
        )
