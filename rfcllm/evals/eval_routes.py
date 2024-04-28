from rfcllm.evals.auth import auth
from rfcllm.evals.prompting import prompting


def eval_routes(app):
    app = auth(app)
    app = prompting(app)
    return app
