import base64, os
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from rfcllm.core import Prompter as prompter
from fastapi.middleware.cors import CORSMiddleware
from rfcllm.services.RFCService import Retriever
from openai import OpenAI
from rfcllm.iam.routes import iam
from rfcllm.search.routes import search
from rfcllm.group.routes import group
from rfcllm.qa.routes import qa

OPENAI_API_KEY = base64.b64decode(os.environ.get("OPENAI_API_KEY", ""))
client = OpenAI(
    api_key=base64.b64decode(
        "c2stUjRZRktpSFJjM0VwMEFVQ0R5bnZUM0JsYmtGSmpYeVE3OVdxYllFc1BMb29Lb1RH"
    ).decode()
)

prompter = prompter.Prompter()

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


retriever = Retriever()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register routes
app = iam(app)
app = search(app)
app = group(app)
app = qa(app)
