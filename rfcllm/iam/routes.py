from datetime import timedelta
from typing import Annotated, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from rfcllm.iam.dto import Token, User
from rfcllm.iam.utils import (
    users_db,
    authenticate_user,
    create_access_token,
    get_current_active_user,
)


def iam(app: Any):
    @app.post("/token", response_model=Token)
    async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    ):
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
    async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)]
    ):
        return current_user

    @app.get("/users/me/items/")
    async def read_own_items(
        current_user: Annotated[User, Depends(get_current_active_user)]
    ):
        return [{"item_id": "Foo", "owner": current_user.username}]

    return app
