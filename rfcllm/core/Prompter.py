from rfcllm.dto import PromptMessageListDTO
from rfcllm.dto.PromptMessageDTO import PromptMessageDTO


class Prompter(object):
    def __init__(self, dialect=""):
        self.dialect = dialect

    def construct_prompt(self, q, ctx):
        prompt_template = """

            \nSystem:
                You will be provided with a document delimited by triple quotes 
                followed by the label \"Question:\"
                and a question. Answer the question using only
                the provided document and cite the passage(s) of the document
                used to answer the question. If you're unable to use
                the contents of the document to answer the question
                accurately, write: "Insufficient information." and if possible
                explain why. Think through this task step by step. Make sure to 
                number and chronologically arrange your chain of thought. Don't 
                use first person.\n
            User:\n
                \"\"\"'{}'\"\"\"
                Question:\n\t\t
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
