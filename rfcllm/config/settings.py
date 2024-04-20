import os
import base64

SYS_SECRET_KEY = os.getenv("SYS_SECRET_KEY", "")
SYS_SK_ALG = os.getenv("SYS_SK_ALG", "HS256")
SYS_ACCESS_TOKEN_TTL = os.getenv("SYS_ACCESS_TOKEN_TTL", 20)
SYS_USERSTORE = os.getenv("SYS_USERSTORE", "")
SECRET_KEY = os.getenv("SECRET_KEY", "")
DEBUG = bool(os.getenv("FLASK_DEBUG", "false"))

SERVER_NAME = os.getenv(
    "SERVER_NAME", "localhost:{0}".format(os.getenv("PORT", "8000"))
)
# SQLAlchemy.
pg_user = os.getenv("POSTGRES_USER", "rfcllm")
pg_pass = os.getenv("POSTGRES_PASSWORD", "password")
pg_host = os.getenv("POSTGRES_HOST", "postgres")
pg_port = os.getenv("POSTGRES_PORT", "5432")
pg_db = os.getenv("POSTGRES_DB", pg_user)
db = f"postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", db)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Redis.
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
INDEX_NAME = os.getenv("INDEX_NAME", "INDEX_NAME")
DOC_PREFIX = os.getenv("DOC_PREFIX", "rfcroot")
SENTINEL_INDEX_NAME = os.getenv("SENTINEL_INDEX_NAME", "idx")

# Celery.
CELERY_CONFIG = {
    "broker_url": REDIS_URL,
    "result_backend": REDIS_URL,
    "include": [],
}

# Custom
AUTHSECRET = os.environ.get("AUTHSECRET")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
RFCPAGESIZE = os.environ.get("RFCPAGESIZE", 4366)
RFCCHUNKOVERLAP = os.environ.get("RFCCHUNKOVERLAP", 100)
OAIENDPOINT = os.environ.get("OAIENDPOINT")
LLAMA2ENDPOINT = os.environ.get("LLAMA2ENDPOINT")
LLAMA2API_KEY = os.environ.get('LLAMA2API_KEY')
OAICHATMODEL = os.environ.get("OAICHATMODEL") or "gpt-4-1106-preview"
OAIPROMPTINGMODEL = os.environ.get("OAIPROMPTINGMODEL") or "gpt-4-1106-preview"
OAIEMBEDDINGMODEL = os.environ.get("OAIEMBEDDINGMODEL")
IETFEP = os.environ.get("IETFEP", "https://datatracker.ietf.org/doc/search")
DTEP = os.environ.get("DTEP", "https://datatracker.ietf.org/")
RFCEP = os.environ.get("RFCEP", "https://www.rfc-editor.org/rfc/")
RFCSEARCHEP = os.environ.get(
    "RFCSEARCHEP", "https://www.rfc-editor.org/search/rfc_search_detail.php"
)
# yikers
RFCSEARCHEPPARAMS = (
    os.environ.get("RFCSEARCHEPPARAMS")
    or "page=All&stream_name=IETF&pubstatus[]=Standards%20Track&pubstatus[]=Best%20Current%20Practice&pubstatus[]=Informational&pubstatus[]=Historic&std_trk=Internet%20Standard&pub_date_type=any&abstract=abson&keywords=keyson&sortkey=Number&sorting=ASC"
)
RFCDELIMITERS = [
    "rfc ",
    "status of this memo",
    "abstract",
    "table of contents",
    "security considerations",
    "authors' addresses",
]
ALGORITHM = "HS256"

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN", "")
AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID", "")
AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET", "")
RFCCLIENTAPP = os.environ.get("RFCCLIENTAPP", "")
GHAUTHCLIENTSECRET = base64.b64decode(os.environ.get("GHAUTHCLIENTSECRET", ""))
GHAUTHCLIENTID = base64.b64decode(os.environ.get("GHAUTHCLIENTID", ""))
GHAUTHREDIRECTEP = os.environ.get("GHAUTHREDIRECTEP", "")
GHAUTHEP = os.environ.get("GHAUTHEP", "")
GHAUTHCLIENTRURI = os.environ.get("GHAUTHCLIENTRURI", "")

# System Strings
INVOCATION_MODES = {"SINGLE": "SINGLE", "COMBINED": "COMBINED"}
