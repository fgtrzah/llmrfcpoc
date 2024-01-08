import re
from typing import Any, Optional
import urllib.parse

import requests
from bs4 import BeautifulSoup
from rfcllm.config.settings import IETFEP, RFCSEARCHEP, RFCSEARCHEPPARAMS


class Retriever:
    def __init__(self, **kwargs):
        self.url = kwargs.get("url") or ""
        self.length_function = kwargs.get("length_function")
        self.chunk_overlap = kwargs.get("chunk_overlap")
        self.chunk_size = kwargs.get("chunk_size")
        self.add_start_index = kwargs.get("add_start_index")
        self.recursive = True
        self.depth = 1
        self.dao: Optional[Any] = None

    def extract_refs(self, text=""):
        urls = re.findall("https?://(?:[-\\w.]|(?:%[\\da-fA-F]{2}))+", text)
        return urls

    def sanitize_text(self, _=""):
        return _

    # async def load(self):
    #     """
    #     TODO: intro aio and multi-core
    #     """
    #     if not self.url:
    #         return []

    #     source_doc = requests.get(self.url).text
    #     converter = Converter()
    #     rfc_annotated_markup = converter.rfc2html(source_doc)
    #     metadataurl = self.url.replace(".txt", ".json")
    #     metadata = DocumentMetaDTO(**requests.get(metadataurl).json())
    #     res = [
    #         DocumentDTO(page_content=source_doc, metadata=metadata).toJSON()
    #     ]

    #     if self.recursive:
    #         outward_links = self.extract_refs(source_doc)
    #         depth = self.depth or 0
    #         count = len(outward_links)

    #         while count > 0 and depth > 0:
    #             ext = outward_links[count - 1]
    #             page_content = requests.get(ext).text.replace("\n", " ")
    #             page_content = page_content.replace("\n\n", " ")
    #             page_content = page_content.replace("\t", " ")

    #             # TODO: text sanitize_text here

    #             metadata: DocumentMetaDTO = requests.get(
    #                 self.url.split(".")[0] + ".json"
    #             ).json()
    #             outward = DocumentDTO(
    #                 page_content=page_content, metadata=metadata
    #             ).toJSON()
    #             res.append(outward)
    #             depth -= 1
    #             count -= 1

    #     return [res, rfc_annotated_markup]

    def retrieve(self, url, **_):
        data = requests.get(url).text
        res = ""
        for line in data.splitlines():
            if not line.startswith(" "):
                res += line
        return res.replace("\n", " ")

    def retrieve_search_rfceietf(self, **kwargs):
        query = kwargs.get("query", "")

        if not query:
            return {"message": "Malformed internal request delegation"}

        headers = {
            "authority": "www.rfc-editor.org",
            "accept": "text/html",
            "accept-language": "en-US",
            "dnt": "1",
            "referer": f"{RFCSEARCHEP}?{RFCSEARCHEPPARAMS}",
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        params = [
            ("title", query or ""),
            ("page", "All"),
            ("abstract", "abson"),
            ("keywords", "keyson"),
            ("pubstatus[]", "Standards Track"),
            ("std_trk", "Internet Standard"),
            ("pubstatus[]", "Best Current Practice"),
            ("pubstatus[]", "Informational"),
            ("pubstatus[]", "Historic"),
            ("pub_date_type", "any"),
            ("stream_name", "IETF"),
        ]

        response = requests.get(f"{RFCSEARCHEP}", params=params, headers=headers)
        res = self.get_extract_json_ietf(search_results=response).get("res")
        return res

    def get_extract_json_ietf(self, **kwargs):
        search_results = kwargs.get("search_results", "")

        if not search_results:
            return {"message": "Malformed internal request delegation"}

        soup = BeautifulSoup(search_results.text, "html.parser")
        table: Any = soup.find("table", {"class": "gridtable"})

        if not table:
            return {"message": "Search document sourcing error"}
        rows = []
        if callable(table.find_all):
            rows = table.find_all("tr")
        res = []
        urls = []

        for _, row in enumerate(rows):
            cells = row.find_all("td")
            links = []
            if len(cells):
                for c in cells:
                    if c.find('a'):
                        links.append(c.find('a')['href'])

            res.append([c.text for c in cells] + links)

        print(urls)

        return {"row": rows, "res": res, "urls": urls}

    def get_json_from_html(self, **kwargs):
        search_results = kwargs.get("search_results", "")

        if not search_results:
            return {"message": "Malformed internal request delegation"}

        soup = BeautifulSoup(search_results.text, "html.parser")
        table: Any = soup.find("table")

        print(table)

        if not table:
            return {"message": "Search document sourcing error"}
        rows = []
        if callable(table.find_all):
            rows = table.find_all("tr")
        res = []
        urls = []

        for _, row in enumerate(rows):
            cells = row.find_all("td")

            if len(cells):
                ir = []
                ir2 = []
                for c in cells:
                    l = None
                    if c.find("a"):
                        l = c.find("a")["href"]
                        ir2.append(f"https://datatracker.ietf.org/api/v1{l}")
                    cr = c.text.replace("\n", " ").strip()
                    ir.append(" ".join(cr.split()))
                urls.append(ir2)
                res.append(ir)

        return {"row": rows, "res": res, "urls": urls}

    def retrieve_search_datatracker(self, **kwargs):
        query = kwargs.get("query", "")
        if not query:
            return {"message": "Malformed internal request delegation"}
        ep = f"{IETFEP}?name={urllib.parse.quote_plus(query)}&sort=&rfcs=on&by=group&group="
        epmeta = f"https://datatracker.ietf.org/api/v1/doc/document/?name={urllib.parse.quote_plus(query)}"

        """2. feed into beautiful soup"""
        epmeta = requests.get(epmeta)
        search_results = requests.get(ep)
        res = self.get_json_from_html(search_results=search_results)
        return [*res, epmeta]

    def get_context(self, openaiservice, dao, query):
        try:
            if not dao or not self.dao:
                return ""

            # Embed the query
            # query_embedding = openaiservice.embed(query)

            # Get the top result from the index
        #     vector_query = VectorQuery(
        #         vector=query_embedding,
        #         vector_field_name="embedding",
        #         return_fields=["content"],
        #         num_results=1,
        #     )
        #     results = self.dao.index.query(vector_query)
        #     content = ""

        #     if len(results) > 1:
        #         content = results[0]["content"]
        #     return content
        except Exception as e:
            raise e
        return {}


retriever = Retriever()
