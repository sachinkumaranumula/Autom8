from typing import List

import requests
from bs4 import BeautifulSoup, ResultSet
from img_crawler_downloader.classes.arch_info import ArchInfo


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
        url = self.__buildSeedApiUrl()
        page = 1
        while url and page <= limit:
            try:
                response = requests.get(url).json()
                all_results.extend(response[resp_conf["identifiers"]["collection"]])
                nextUrl = response[resp_conf["identifiers"]["pagination"]["nextUrl"]]
                if nextUrl:
                    url = self.__absoluteUrl(response[resp_conf["identifiers"]["pagination"]["nextUrl"]])
                else:
                    url = f"{url}&{response[resp_conf["identifiers"]["pagination"]["urlPrefix"]]}={page}"
                page += 1
            except Exception as e:
                print(e)
                break
        return all_results

    def getArchInfos(self) -> List[ArchInfo]:
        api_json = self.__getArchResults()
        resp_conf = self.config["response"]
        nested = resp_conf["identifiers"].get("nested")
        item_fields = resp_conf["identifiers"]["item"]
        arch_infos: List[ArchInfo] = []
        for item in api_json:
            print(item)
            if nested:
                item = item[nested["item"]]
                if nested["additional"]:
                    item = item[nested["additional"]]
            arch_info: ArchInfo = {"title": item[item_fields["title"]],
                                   "summary": item[item_fields["summary"]],
                                   "url": self.__buildItemUrl(item[item_fields["url"]])}
            if "thumbnail" in item_fields:
                arch_info.update({"thumbnail": self.__buildItemUrl(item[item_fields["thumbnail"]])})
            if "categories" in item_fields:
                arch_info.update({"categories": item[item_fields["categories"]]})
            if "products" in item_fields:
                arch_info.update({"products": item[item_fields["products"]]})
            arch_infos.append(arch_info)
        return arch_infos

    def __str__(self) -> str:
        return f"config=> {self.config}"


class ApiWebCrawler:

    def __init__(self, config: dict) -> None:
        self.config = config

    def findItemsOfInterest(self, html: str) -> ResultSet:
        soup = BeautifulSoup(html, "html5lib")
        return soup.find_all("div")

    def __str__(self) -> str:
        return f"config=> {self.config}"
