import os
from typing import Any
from fastapi import Request
from fastapi_sso.sso.github import GithubSSO

GHAUTHCLIENTID = os.environ.get("GHAUTHCLIENTID", "")
GHAUTHCLIENTSECRET = os.environ.get("GHAUTHCLIENTSECRET", "")

sso = GithubSSO(
    client_id=GHAUTHCLIENTID,
    client_secret=GHAUTHCLIENTSECRET,
    redirect_uri=f"https://127.0.0.1:8000/auth/callback",
    allow_insecure_http=True,
)


def iam(app: Any):
    @app.get("/auth/login")
    async def auth_login():
        """Initialize auth and redirect"""
        with sso:
            return await sso.get_login_redirect()

    @app.get("/auth/callback")
    async def auth_callback(request: Request):
        """Verify login"""
        with sso:
            user = await sso.verify_and_process(request)
            return user

    return app
