from typing import Any


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

    def construct_sysff_message(self, ctx: str = ""):
        prompt_template = "System:\n\nYou're an intelligent subject matter expert specializing in comprehending RFC Documents and the standards and protocols that they put forth to govern many parts of the internet and networking best practices. You're also well versed in coming up with feed-forward style inquisitive questions designed to help bolster the understanding of the contents in an RFC document, Your task is to utilize the text delimited by \"####\" and then perform a series of procedural actions based on the context within the delimited text.\n\nEND SYSTEM INSTRUCTIONS\n\n####\n'{}'\n####\n\nTask:\nYour first task is to suggest some questions about the RFC inside #### ... #### that can help me get inspiration for what to ask, the goal is to foster efficient understanding of that RFC in the fastest way possible. Do not fabricate anything, and utilize only the text inside the delimited strings. If you don't know, explicitly state you dont know and provide a brief explanation clarifying why you can't answer.\n\nSuggested questions:"
        return [
            {
                "role": "system",
                "content": [{"text": prompt_template.format(ctx), "type": "text"}],
            }
        ]

    def construct_message(self, prompt: str = "", ctx: list[Any] = []):
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
