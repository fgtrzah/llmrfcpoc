from typing import Any
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Any


class User(BaseModel):
    username: str
    email: Any
    full_name: Any
    disabled: Any


class UserInDB(User):
    hashed_password: str
