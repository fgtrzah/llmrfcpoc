import os

SYS_SECRET_KEY = os.getenv("SYS_SECRET_KEY", "") 
SYS_SK_ALG = os.getenv("SYS_SK_ALG", "HS256") 
SYS_ACCESS_TOKEN_TTL = os.getenv("SYS_ACCESS_TOKEN_TTL", 20)
SYS_USERSTORE = os.getenv("SYS_USERSTORE", "")


