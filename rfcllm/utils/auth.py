from datetime import datetime, timedelta
from rfcllm.config.settings import SYS_SECRET_KEY, SYS_SK_ALG
from rfcllm.dao.user import get_user
from jose import jwt


def verify_password(pwd_context, plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(pwd_context, password):
    return pwd_context.hash(password)


def authenticate_user(pwd_context, user_store, username: str, password: str):
    user = get_user(user_store, username)
    if not user:
        return False
    if not verify_password(pwd_context, password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SYS_SECRET_KEY, algorithm=SYS_SK_ALG)
    return encoded_jwt
