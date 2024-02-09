# import os
# from typing import Any
# from fastapi import Request
# from fastapi_sso.sso.github import GithubSSO

# GHAUTHCLIENTID = os.environ.get("GHAUTHCLIENTID", "")
# GHAUTHCLIENTSECRET = os.environ.get("GHAUTHCLIENTSECRET", "")

# sso = GithubSSO(
#     client_id=GHAUTHCLIENTID,
#     client_secret=GHAUTHCLIENTSECRET,
#     redirect_uri=f"https://127.0.0.1:8080/auth/callback",
#     allow_insecure_http=True,
# )


# def iam(app: Any):
#     @app.get("/auth/token")
#     async def auth_token():
#         """Initialize auth and redirect"""
#         with sso:
#             return await sso.get_login_redirect()

#     @app.get("/auth/login")
#     async def auth_login():
#         """Initialize auth and redirect"""
#         with sso:
#             return await sso.get_login_redirect()

#     @app.get("/auth/callback")
#     async def auth_callback(request: Request):
#         """Verify login"""
#         with sso:
#             user = await sso.verify_and_process(request)
#             return user

#     return app



import base64
import json
import requests

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from rfcllm.config.settings import GHAUTHCLIENTID, GHAUTHCLIENTSECRET, GHAUTHEP, GHAUTHREDIRECTEP

# GitHub App credentials
CLIENT_ID = GHAUTHCLIENTID
CLIENT_SECRET = GHAUTHCLIENTSECRET
REDIRECT_URI = GHAUTHREDIRECTEP

def iam(app):
    @app.get('/auth/login')
    def auth_login():
        # Redirect the user to GitHub for authentication
        return RedirectResponse(f'{GHAUTHEP}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}')

    @app.get('/auth/callback')
    async def auth_callback(request: Request):
        print(request)
        # Exchange the authorization code for an access token
        code = request.query_params.get('code')
        print('CP: ', code)
        response = requests.post('https://github.com/login/oauth/access_token', {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'redirect_uri': REDIRECT_URI
        }, headers={'Accept': 'application/json'}).json()
        
        access_token = response.get('access_token')
       
        if access_token:
            user_response = requests.get(
                'https://api.github.com/user', 
                headers={'Authorization': f'Bearer {access_token}'}
            )
            return user_response.json()
        else:
            raise HTTPException(status_code=400, detail='Authentication failed')

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code, 
            content={'error': exc.detail}
        )

    return app
