"""Isolated unit test for BasicAuthMiddleware, using a minimal throwaway app
rather than the shared rag_platform.api.app singleton — avoids depending on
when/how that module's cached middleware stack gets built.
"""

import base64

from fastapi import FastAPI
from fastapi.testclient import TestClient

from rag_platform.api.auth import BasicAuthMiddleware
from rag_platform.config import Settings


def _make_client(user: str, password: str) -> TestClient:
    app = FastAPI()

    @app.get("/ping")
    def ping() -> dict:
        return {"ok": True}

    app.add_middleware(
        BasicAuthMiddleware,
        settings=Settings(basic_auth_user=user, basic_auth_password=password),
    )
    return TestClient(app)


def _basic_header(user: str, password: str) -> dict:
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def test_disabled_when_credentials_empty():
    client = _make_client(user="", password="")
    assert client.get("/ping").status_code == 200


def test_rejects_missing_credentials():
    client = _make_client(user="admin", password="s3cret")
    response = client.get("/ping")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == 'Basic realm="rag-platform"'


def test_rejects_wrong_credentials():
    client = _make_client(user="admin", password="s3cret")
    response = client.get("/ping", headers=_basic_header("admin", "wrong"))
    assert response.status_code == 401


def test_accepts_correct_credentials():
    client = _make_client(user="admin", password="s3cret")
    response = client.get("/ping", headers=_basic_header("admin", "s3cret"))
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_env_var_names_actually_match_the_settings_fields(monkeypatch):
    """Regression test: constructing Settings via kwargs (as the tests above
    do) can't catch a mismatch between a field name and the env var name
    pydantic-settings actually looks for — this bit us for real once (env
    vars were named RAG_PLATFORM_BASIC_AUTH_USER/PASSWORD, but with no
    env_prefix configured, the field `basic_auth_user` only ever matches
    bare `BASIC_AUTH_USER`). This test goes through the real env-var path.
    """
    monkeypatch.setenv("BASIC_AUTH_USER", "admin")
    monkeypatch.setenv("BASIC_AUTH_PASSWORD", "s3cret")

    settings = Settings()

    assert settings.basic_auth_user == "admin"
    assert settings.basic_auth_password == "s3cret"
