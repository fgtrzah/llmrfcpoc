import json
import re


def pluck_urls(text=""):
    return re.findall("(?P<url>https?://[^\\s]+)", text)


def convert_message_list_to_text(messages: list) -> str:
    print(messages[0])
    B_INST, E_INST = "[INST]", "[/INST]"
    B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
    text = ""

    if messages and messages[0]["role"] == "system":
        messages = [
            {
                "role": messages[1]["role"],
                "content": B_SYS
                + messages[0]["content"]
                + E_SYS
                + messages[1]["content"],
            }
        ] + messages[2:]

    texts = []
    for prompt, answer in zip(messages[::2], messages[1::2]):
        texts.append(
            f"{B_INST} {(prompt['content']).strip()} {E_INST} {(answer['content']).strip()} "
        )

    text = "</s><s>".join(texts)
    text = "<s>" + text + " </s>"
    return text
