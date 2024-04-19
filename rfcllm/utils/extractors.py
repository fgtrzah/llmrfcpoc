import re


def pluck_urls(text=""):
    return re.findall("(?P<url>https?://[^\\s]+)", text)
