from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

# Instantiate the class
app = FastAPI()

users_db = {
    "system": {
        "username": "system",
        "full_name": "system",
        "email": "admin@fgtrz.com",
        "hashed_password": "67e375717d8d06e5ec5feac9b92e97a4",
        "disabled": False,
    }
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Define a GET method on the specified endpoint
@app.get("/")
def hello():
    return {"result": "Welcome to FastAPI"}
