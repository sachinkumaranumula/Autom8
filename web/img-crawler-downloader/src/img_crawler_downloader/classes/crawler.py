from typing import List

import requests
from bs4 import BeautifulSoup, ResultSet
from img_crawler_downloader.classes.arch_info import ArchInfo


class ArchApiCrawler:

    def __init__(self, config: dict) -> None:
        self.config = config

    def __buildSeedApiUrl(self) -> str:
        req_conf = self.config["request"]
        return f"{self.__absoluteUrl(req_conf["apiUrl"])}/?locale={req_conf["locale"]}"

    def __absoluteUrl(self, url) -> str:
        req_conf = self.config["request"]
        return f"{req_conf["baseUrl"]}{url}"

    def __getArchResults(self) -> list:
        req_conf = self.config["request"]
        resp_conf = self.config["response"]
        limit = req_conf["query"]["pagination"]["limit"]
        all_results = []
        url = self.__buildSeedApiUrl()
        page = 0
        while url and page < limit:
            try:
                response = requests.get(url).json()
                all_results.extend(response[resp_conf["identifiers"]["collection"]])
                url = self.__absoluteUrl(response[resp_conf["identifiers"]["pagination"]["nextUrl"]])
                page += 1
            except Exception as e:
                print(e)
                break
        print(all_results)
        return all_results

    def getArchInfos(self) -> List[ArchInfo]:
        api_json = self.__getArchResults()
        arch_infos: List[ArchInfo] = []
        for item in api_json:
            arch_infos.append({"title": item["title"],
                               "summary": item["summary"],
                               "thumbnail": self.__absoluteUrl(item["thumbnail_url"]),
                               "url": self.__absoluteUrl(item["url"]),
                               "categories": item["azure_categories"],
                               "products": item["products"]})
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
