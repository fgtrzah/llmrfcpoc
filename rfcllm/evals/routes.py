from rfcllm.evals.auth import auth
from rfcllm.evals.prompting import prompting


def evals(app):
    app = auth(app)
    app = prompting(app)
    return app
