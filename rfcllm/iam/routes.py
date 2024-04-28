import base64
import json
from urllib.parse import urlencode
import requests

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from rfcllm.config.settings import (
    GHAUTHCLIENTID,
    GHAUTHCLIENTSECRET,
    GHAUTHEP,
    GHAUTHREDIRECTEP,
    GHAUTHCLIENTRURI,
)

# GitHub App credentials
CLIENT_ID = GHAUTHCLIENTID
CLIENT_SECRET = GHAUTHCLIENTSECRET
REDIRECT_URI = GHAUTHREDIRECTEP


def iam(app):
    @app.get("/auth/login")
    def auth_login():
        # Redirect the user to GitHub for authentication
        return RedirectResponse(f"{GHAUTHEP}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}")

    @app.get("/auth/callback")
    async def auth_callback(request: Request):
        # Exchange the authorization code for an access token
        code = request.query_params.get("code")
        response = requests.post(
            "https://github.com/login/oauth/access_token",
            {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code,
                "redirect_uri": REDIRECT_URI,
            },
            headers={"Accept": "application/json"},
        ).json()

        access_token = response.get("access_token")

        if access_token:
            user_response = requests.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            # return user_response.json()
            state = urlencode({"data": user_response.json()})
            dest_url = f"http://localhost:5173?#state={state}"
            return RedirectResponse(dest_url)
        else:
            raise HTTPException(status_code=400, detail="Authentication failed")

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

    return app
