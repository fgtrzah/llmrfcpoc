def prompting(app):
    @app.get("/evals/prompting/index")
    def evals_prompting_index():
        return {"response": "prompting"}

    @app.get("/evals/prompting/zeroshot")
    def evals_prompting_zeroshot():
        return {"response": "prompting"}

    return app
