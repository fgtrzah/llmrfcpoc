import requests
from bs4 import BeautifulSoup


class RFCRetriever(object):
    def __init__(self, url="") -> None:
        self.url = url
        self.doc = requests.get(self.url).content
        self.client = BeautifulSoup(self.doc, "html.parser")

    def load(self):
        return [t.get_text() for t in self.client.find_all("pre", "newpage")]
