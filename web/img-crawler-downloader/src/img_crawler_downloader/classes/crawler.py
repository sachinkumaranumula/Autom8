import uuid
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
                        print("No more Next Page")
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
                    print(item)
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
            return self.__buildItemUrl(item[item_fields[fieldName]])
        return "Unknown"

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
