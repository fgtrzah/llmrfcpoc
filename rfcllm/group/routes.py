import requests

from typing import Any
from rfcllm.config.settings import DTEP


def group(app: Any):
    @app.post("/group/groupmenu")
    async def group_groupmenu():
        res = requests.get(f"{DTEP}group/groupmenu.json").json()
        return {"result": res}

    return app
