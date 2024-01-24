from fastapi.datastructures import QueryParams
from fastapi.responses import RedirectResponse
import requests
from datetime import timedelta
from typing import Annotated, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from rfcllm.config.settings import GHAUTHEP, RFCCLIENTAPP
from rfcllm.iam.dto import Token, User
from rfcllm.iam.utils import (
    get_oauth,
    users_db,
    authenticate_user,
    create_access_token,
    get_current_active_user,
)


def iam(app: Any):
    @app.get('/oauth/access_token', response_model=RedirectResponse)
    async def oauth_access_token(code: str | None = None):
        res = requests.post(
            f'{GHAUTHEP}/login/oauth/access_token',
            json={
                'client_id': GHAUTHCLIENTID,
                'client_secret': GHAUTHCLIENTSECRET,
                'code': code,
                'redirect_uri': f'http://127.0.0.1/8000/oauth/token'

            }
        ) 
    
   
    @app.get('/oauth/callback', response_model=RedirectResponse)
    async def oauth_callback(code: str | None = None):
        if code:
            return RedirectResponse(f'{RFCCLIENTAPP}?code={code}')
        return RedirectResponse(f'{RFCCLIENTAPP}/unauthorized')
         

    @app.get("/login/oauth", response_class=RedirectResponse)
    async def login_auth():
        gh_client_id = ''
        gh_redirect_uri = ''
        gh_state = ''

        return RedirectResponse(
            f'{GHAUTHEP}?client_id={gh_client_id}&state={gh_state}&redirect_uri={gh_redirect_uri}'
        )

    @app.post("/token", response_model=Token)
    async def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
        print(form_data.username, form_data.password)
        user = authenticate_user(users_db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    @app.get("/users/me/", response_model=User)
    async def users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
        return current_user

    @app.get("/users/me/items/")
    async def users_me_items(
        current_user: Annotated[User, Depends(get_current_active_user)]
    ):
        return [{"item_id": "Foo", "owner": current_user.username}]
    
    return app
