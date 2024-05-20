from uuid import uuid4
import os

from fastapi.responses import FileResponse

from rfcllm.config.settings import ENDPOINT
from rfcllm.dto.DatasetRequestDTO import DatasetRequestDTO


def datasets(app):
    @app.get("/datasets/index")
    def datasets_index():
        filenames = os.listdir("./rfcllm/datasets/data")

        return {
            "data": {
                "type": "MetaEndpoint",
                "id": uuid4(),
                "attributes": {f: "./rfcllm/datasets/data/" + f for f in filenames},
            }
        }

    @app.get("/datasets/{id}")
    def datasets_by_id(id: str):
        print(id)
        ds = datasets_index().get("data", {}).get("attributes", {})
        print(ds.get(id))
        loc = ds.get(id)
        with open("./rfcllm/datasets/data/" + id) as f:
            r = f.read()
        return {"data": {"type": "FileResponse", "id": loc, "content": r}}

    return app
