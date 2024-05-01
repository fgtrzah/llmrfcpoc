from __future__ import annotations
import json
import re
from typing import Any

import errno
import os
import platform
import re
import stat
import sys
from contextlib import suppress
from decimal import Decimal
from enum import Enum
from importlib.metadata import version
from pathlib import Path
from types import TracebackType
from typing import Any, Callable, Literal, TextIO, cast

import colorama
from pydantic import StrictBool

INDENT = " " * 2
HLINE = "-" * 42


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
