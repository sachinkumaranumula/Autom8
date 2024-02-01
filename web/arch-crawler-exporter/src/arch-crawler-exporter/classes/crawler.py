import re
import uuid
from typing import List
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup, ParserRejectedMarkup
from classes.arch import ArchInfo


class ArchApiCrawler:

    def __init__(self, config: dict) -> None:
        self.config = config

    def __buildSeedApiUrl(self) -> str:
        req_conf = self.config["request"]
        return self.__absoluteUrl(req_conf["apiUrl"])

    def __absoluteUrl(self, url) -> str:
        req_conf = self.config["request"]
        return f"{req_conf["baseUrl"]}{url}"

    def __buildItemUrl(self, url) -> str:
        resp_conf = self.config["response"]
        if resp_conf["absoluteUrls"]:
            return url
        else:
            return self.__absoluteUrl(url)

    def __getArchResults(self) -> list:
        req_conf = self.config["request"]
        resp_conf = self.config["response"]
        limit = req_conf["query"]["pagination"]["limit"]
        all_results = []
        seed_url = self.__buildSeedApiUrl()
        url = seed_url
        page = 1
        total = 1
        count = 0
        while count < total and page <= limit:
            try:
                response = requests.get(url).json()
                collection = response[resp_conf["identifiers"]["collection"]]
                all_results.extend(collection)
                count += len(collection)
                if "nested" in resp_conf["identifiers"]:
                    metadata = response[resp_conf["identifiers"]["nested"]["total"]]
                    total = metadata[resp_conf["identifiers"]["total"]]
                else:
                    total = response[resp_conf["identifiers"]["total"]]
                if "nextUrl" in resp_conf["identifiers"]["pagination"]:
                    if resp_conf["identifiers"]["pagination"]["nextUrl"] in response:
                        nextUrl = response[resp_conf["identifiers"]["pagination"]["nextUrl"]]
                        if nextUrl:
                            url = self.__absoluteUrl(response[resp_conf["identifiers"]["pagination"]["nextUrl"]])
                    else:
                        break
                else:
                    url = f"{seed_url}&{resp_conf["identifiers"]["pagination"]["urlPrefix"]}={page}"
                page += 1
            except Exception as e:
                print("Exception Occured", e)
                break
        return all_results

    def getArchInfos(self) -> List[ArchInfo]:
        api_json = self.__getArchResults()
        resp_conf = self.config["response"]
        nested = resp_conf["identifiers"].get("nested")
        item_fields = resp_conf["identifiers"]["item"]
        arch_infos: List[ArchInfo] = []
        for item in api_json:
            try:
                if nested:
                    item = item[nested["item"]]
                    if nested["displayInfo"]:
                        item = item[nested["displayInfo"]]
                arch_info: ArchInfo = {"id": str(uuid.uuid4()),
                                       "title": self.__getFieldValue(item, item_fields, "title"),
                                       "summary": self.__getFieldValue(item, item_fields, "summary"),
                                       "url": self.__buildItemUrl(self.__getFieldValue(item, item_fields, "url"))}
                if "thumbnail" in item_fields:
                    arch_info.update({"thumbnail": self.__buildItemUrl(item[item_fields["thumbnail"]])})
                if "categories" in item_fields:
                    arch_info.update({"categories": item[item_fields["categories"]]})
                if "products" in item_fields:
                    arch_info.update({"products": item[item_fields["products"]]})
                arch_infos.append(arch_info)
            except KeyError:
                continue
        return arch_infos

    def __getFieldValue(self, item, item_fields, fieldName):
        if item_fields[fieldName] in item:
            return item[item_fields[fieldName]]
        return "Unknown"

    def __str__(self) -> str:
        return f"config=> {self.config}"


class ArchWebCrawler:
    HEADERS = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Max-Age": "3600",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
    }

    def __init__(self, config: dict) -> None:
        self.config = config

    def __findSelectorValue(self,
                            url: str,
                            element: str,
                            findAttribute: str,
                            findRegex: str,
                            valueAttribute: str) -> str:
        try:
            req = requests.get(url, self.HEADERS)
            soup = BeautifulSoup(req.content, "html.parser", from_encoding="iso-8859-1")
            img = soup.find(element, alt=re.compile(findRegex))
            if img is not None:
                return img[valueAttribute]  # type: ignore
            else:
                return ""
        except ParserRejectedMarkup:
            print("Cannot Parse", url)
            return ""

    def enrichWithSelectors(self, arch_infos):
        selectors = self.config["selectors"]
        for key in selectors:
            selector = selectors[key]
            for arch_info in arch_infos:
                url = arch_info[selector["archUrlRef"]]
                scrapedValue = self.__findSelectorValue(
                    url,
                    selector["element"],
                    selector["findAttribute"],
                    selector["findRegex"],
                    selector["valueAttribute"],
                )
                if scrapedValue:
                    if bool(urlparse(scrapedValue).netloc):
                        arch_info[key] = scrapedValue
                    else:
                        parse_result = urlparse(url)
                        arch_info[key] = f"{parse_result.scheme}://{parse_result.netloc}{scrapedValue}"

    def __str__(self) -> str:
        return f"config=> {self.config}"
