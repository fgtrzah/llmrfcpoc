from rfcllm.evals.auth import auth

def eval_routes(app):
    app = auth(app)
    return app
