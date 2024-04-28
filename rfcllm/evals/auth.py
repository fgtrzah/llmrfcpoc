from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import RedirectResponse
import requests

from rfcllm.config.settings import GHAUTHCLIENTID, GHAUTHCLIENTSECRET, GHAUTHEP

app = FastAPI()

# GitHub App credentials
CLIENT_ID = GHAUTHCLIENTID
CLIENT_SECRET = GHAUTHCLIENTSECRET
REDIRECT_URI = "https://127.0.0.1:8080/auth/callback"
FRONTEND_REDIRECT_URI = "http://localhost:5173/auth/callback"


def auth(app):
    @app.get("/evals/auth/login")
    def login():
        github_redirect_url = (
            f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
        )
        return RedirectResponse(github_redirect_url)

    @app.get("/evals/auth/callback")
    async def callback(request: Request):
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
        )

        access_token = response.json().get("access_token")

        if access_token:
            profile = await requests.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access_token}"},
            ).json()
            redirect_url = f"{FRONTEND_REDIRECT_URI}?access_token={access_token}&profile={profile}"
            return RedirectResponse(redirect_url)
        else:
            raise HTTPException(status_code=400, detail="Authentication failed")

    return app
