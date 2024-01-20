import requests

from typing import Annotated, Any
from fastapi import Depends
from rfcllm.config.settings import DTEP
from rfcllm.iam.dto import User
from rfcllm.iam.utils import get_current_active_user


def group(app: Any):
    @app.post("/group/groupmenu")
    async def group_groupmenu(
        current_user: Annotated[User, Depends(get_current_active_user)]
    ):
        res = requests.get(f"{DTEP}group/groupmenu.json").json()
        return {"result": res}

    return app
