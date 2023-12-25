from datetime import datetime, timedelta
from typing import Annotated, Any
import base64, os
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from rfcllm.dto.InquiryDTO import InquiryDTO

from rfcllm.dto.SearchRequestDTO import SearchRequestDTO
from rfcllm.services.RFCService import Retriever

# imports
import time  # for measuring time duration of API calls
from openai import OpenAI

OPENAI_API_KEY = base64.b64decode(os.environ.get("OPENAI_API_KEY", ""))
client = OpenAI(
    api_key=base64.b64decode(
        "c2stUjRZRktpSFJjM0VwMEFVQ0R5bnZUM0JsYmtGSmpYeVE3OVdxYllFc1BMb29Lb1RH"
    ).decode()
)  # for OpenAI API calls

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}
retriever = Retriever()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload: Any = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data: Any = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
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


@app.post("/search/query/ietf")
async def search_ietf(search: SearchRequestDTO):
    res = retriever.retrieve_search_rfceietf(query=search.query)
    return {"results": res}


@app.post("/qa/single")
async def search_ietf(
    current_user: Annotated[User, Depends(get_current_active_user)], inquiry: InquiryDTO
):
    # Example of an OpenAI ChatCompletion request
    # https://platform.openai.com/docs/guides/chat
    query, context = inquiry.dict()
    res = []

    # record the time before the request is sent
    start_time = time.time()

    # send a ChatCompletion request to count to 100
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "Count to 100, with a comma between each number and no newlines. E.g., 1, 2, 3, ...",
            }
        ],
        temperature=0,
    )
    # calculate the time it took to receive the response
    response_time = time.time() - start_time

    # print the time delay and text received
    print(f"Full response received {response_time:.2f} seconds after request")
    print(f"Full response received:\n{completion}")

    res.append(completion)

    return {
        "results": res,
        "query": query,
        "context": context,
        "current_user": current_user,
    }


"""

@qa.post("/single")
@authorized
def single():
    req_data = request.get_json()
    q = req_data["query"]
    ctx = req_data["context"]
    url = ctx if is_url(ctx) else ""

    try:
        ref_text_meta = (
            DocumentMetaDTO(**requests.get(url.replace("txt", "json")).json())
            or ""
        )
        p = prompter.construct_prompt(q, ref_text_meta)
        ctx = RFCRetriever(url=url.replace('txt', 'html')).load()
        response = oaiservice.client.chat.completions.create(
            model='gpt-4-1106-preview',
            messages=prompter.construct_message(p, ctx),
        )

        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "message": jsonify({'error': e})
        }



"""
