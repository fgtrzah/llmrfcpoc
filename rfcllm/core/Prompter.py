from typing import Any


class Prompter(object):
    def contruct_prompt(self, prompt: Any, query: str, context: str):
        return prompt.format(query, context)

    def construct_template(self):
        pass
