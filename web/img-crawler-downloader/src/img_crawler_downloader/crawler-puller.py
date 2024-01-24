#!/usr/bin/env python3
# python3 -m pip install -U {packages-to-install}
# Run:
# python crawler-puller.py
import argparse
import csv
import json
import os.path
import time

import requests
from bs4 import BeautifulSoup, ResultSet

FIELD_TITLE = "title"
FIELD_SUMMARY = "summary"
FIELD_THUMBNAIL = "thumbnail"
FIELD_URL = "url"
FIELD_CATEGORIES = "categories"
FIELD_PRODUCTS = "products"
FIELD_NAMES = [FIELD_TITLE, FIELD_SUMMARY, FIELD_THUMBNAIL, FIELD_URL, FIELD_CATEGORIES, FIELD_PRODUCTS]


def get_config() -> dict:
    configParser = argparse.ArgumentParser()
    configParser.add_argument(
        "-cf",
        "--config_file",
        help="config file name",
        default="",
        type=str,
        required=True,
    )
    configArgs = configParser.parse_known_args()
    config = json.load(open(configArgs[0].config_file))
    return config


def crawl_and_pull(config: dict):
    icd = ImageCrawlerDownloader(config)
    icd.saveArchInfos()


def dump_dict(dict, filename):
    with open(filename, "w") as fp:
        json.dump(dict, fp, indent=2)


def arch_info(title, summary, thumbnailUrl, url, categories, products) -> dict:
    return {
        FIELD_TITLE: title,
        FIELD_SUMMARY: summary,
        FIELD_THUMBNAIL: thumbnailUrl,
        FIELD_URL: url,
        FIELD_CATEGORIES: categories,
        FIELD_PRODUCTS: products
    }


class ImageCrawlerDownloader:

    def __init__(self, config: dict) -> None:
        self.config = config

    def buildWebUrl(self) -> str:
        crawler = self.config["crawler"]
        # filter = crawler["query"]["filter"]
        # params = crawler["query"]["params"]
        return f"{crawler["baseUrl"]}"

    def buildSeedApiUrl(self) -> str:
        crawler = self.config["crawler"]
        return f"{self.absoluteUrl(crawler["apiUrl"])}/?locale={crawler["locale"]}"

    def absoluteUrl(self, url) -> str:
        crawler = self.config["crawler"]
        return f"{crawler["baseUrl"]}{url}"

    def getArchResults(self) -> list:
        limit = self.config["crawler"]["limit"]
        all_results = []
        url = self.buildSeedApiUrl()
        page = 0
        while url and page < limit:
            try:
                response = requests.get(url).json()
                all_results.extend(response['results'])
                url = self.absoluteUrl(response['@nextLink'])
                page += 1
            except Exception as e:
                print("Error calling arch catalog", e)
                break
        print(all_results)
        return all_results

    def getWebPage(self, url: str) -> str:
        response = requests.get(url)
        print(response.request.headers)
        print(response.text)
        return response.text

    def findItemsOfInterest(self, html: str) -> ResultSet:
        soup = BeautifulSoup(html, "html5lib")
        return soup.find_all("div")

    def getArchInfos(self) -> list:
        api_json = self.getArchResults()
        arch_infos = []
        for item in api_json:
            arch_infos.append(arch_info(item["title"], item["summary"], self.absoluteUrl(item["thumbnail_url"]),
                                        self.absoluteUrl(item["url"]), item["azure_categories"], item["products"]))
        return arch_infos

    def saveArchInfos(self) -> None:
        arch_infos = self.getArchInfos()
        archsLocation = os.path.join(self.downloadLocation(), "archs.csv")
        with open(archsLocation, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES)
            writer.writeheader()
            writer.writerows(arch_infos)

    def downloadLocation(self) -> str:
        downloadLocation = self.config["downloader"]["location"]
        os.makedirs(downloadLocation, exist_ok=True)
        return downloadLocation

    def downloadImage(self, imgUrl: str) -> None:
        imgData = requests.get(imgUrl).content
        imgLocation = os.path.join(self.downloadLocation(), os.path.basename(imgUrl))
        with open(imgLocation, 'wb') as handler:
            handler.write(imgData)

    def __str__(self) -> str:
        return f"config=> {self.config}"


def main():
    startTime = time.time()
    config = get_config()
    crawl_and_pull(config)
    endTime = time.time()
    print(f"Total Time:{endTime - startTime}")


if __name__ == "__main__":
    exit(main())
