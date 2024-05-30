from __future__ import annotations
import re
from typing import Any
import re
import sys
from typing import Any, TextIO
import colorama
from pydantic import StrictBool

INDENT = " " * 2
HLINE = "-" * 42


def remove_blank_and_footer_lines(file_contents):
    """
    Removes blank lines and lines resembling page footers from the given file contents.

    Args:
        file_contents (str): The contents of the file.

    Returns:
        str: The file contents with blank lines and page footers removed.
    """
    footer_pattern = r"^[A-Za-z]+\s+\w+\s+\w+\s+\[\w+\s\d+\]$"
    lines = file_contents.split("\n")
    filtered_lines = [
        line for line in lines if line.strip() and not re.match(footer_pattern, line)
    ]
    filtered_contents = "\n".join(filtered_lines)
    return filtered_contents


class Style:
    """Common color styles."""

    OK = [colorama.Fore.GREEN, colorama.Style.BRIGHT]
    WARNING = [colorama.Fore.YELLOW, colorama.Style.BRIGHT]
    IGNORE = [colorama.Fore.CYAN]
    DANGER = [colorama.Fore.RED, colorama.Style.BRIGHT]
    RESET = [colorama.Fore.RESET, colorama.Style.RESET_ALL]


def printf(
    action: str,
    msg: Any = "",
    style: list[str] | None = None,
    indent: int = 10,
    quiet: bool | StrictBool = False,
    file_: TextIO = sys.stdout,
) -> str | None:
    """Print string with common format."""
    if quiet:
        return None
    _msg = str(msg)
    action = action.rjust(indent, " ")
    if not style:
        return action + _msg

    out = style + [action] + Style.RESET + [INDENT, _msg]
    print(*out, sep="", file=file_)
    return None


def printf_exception(
    e: Exception, action: str, msg: str = "", indent: int = 0, quiet: bool = False
) -> None:
    """Print exception with common format."""
    import sys

    if not quiet:
        print("", file=sys.stderr)
        printf(action, msg=msg, style=Style.DANGER, indent=indent, file_=sys.stderr)
        print(HLINE, file=sys.stderr)
        print(e, file=sys.stderr)
        print(HLINE, file=sys.stderr)


def pluck_urls(text=""):
    return re.findall("(?P<url>https?://[^\\s]+)", text)


def sanitize_url(url):
    invalid_chars = "<>|.{}\\`^"
    if url[-1] in ".,;:!?\"'<>()[]{}|\\`~^&*#$%":
        url = url[:-1]
    if url[0] in ".,;:!?\"'<>()[]{}|\\`~^&*#$%":
        url = url[0]
    return url.strip(invalid_chars)


def extract_urls(text):
    url_pattern = re.compile(r"(https?://[^\s]+)")
    urls = re.findall(url_pattern, text)
    urls = [sanitize_url(u) for u in urls]
    return urls


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
