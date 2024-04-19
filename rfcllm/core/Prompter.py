from rfcllm.dto import PromptMessageListDTO
from rfcllm.dto.PromptMessageDTO import PromptMessageDTO


class Prompter(object):
    def __init__(self, dialect=""):
        self.dialect = dialect

    def construct_prompt(self, q, ctx):
        prompt_template = """
            System:
                You will be provided with a document delimited by triple quotes
                and a question. Answer the question using only
                the provided document and to cite the passage(s) of the document
                used to answer the question. If the document does not contain
                the information needed to answer this question then simply
                write: "Insufficient information.".
            User:
                \"\"\"'{}'\"\"\"
                Question:
        """
        return prompt_template.format(ctx) + q

    def construct_message(self, prompt: str = "", ctx: list[str] = []):
        msg = {
            "role": "system",
            "content": "You're a helpful assistant providing answers based on the following \
                    context without hallucinations.",
        }
        res = [msg]

        for i in ctx:
            res.append({"role": "user", "content": i.replace("\n", " ")})

        res.append({"role": "user", "content": prompt})

        return res


prompter = Prompter()
