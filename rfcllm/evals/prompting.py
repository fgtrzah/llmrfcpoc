def prompting(app):
    @app.get("/evals/prompting/index")
    def evals_prompting_index():
        return {"response": "prompting"}

    return app
