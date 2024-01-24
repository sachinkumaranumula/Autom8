#!/usr/bin/env python3
# python3 -m pip install -U {packages-to-install}
# Run:
# python crawler-puller.py
import argparse
import json
import os.path
import time

import requests
from bs4 import BeautifulSoup, ResultSet


def input():
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
    icd = ImageCrawlerDownloader(config)
    url = icd.buildSeedApiUrl()
    print("GET: ", url)
    apiJson = icd.getApi(url)

    for item in apiJson["results"]:
        print(item["thumbnail_url"])
        icd.downloadImage("downloaded", f"{config["crawler"]["baseUrl"]}/{item["thumbnail_url"]}")

    with open("response.json", "w") as fp:
        json.dump(apiJson, fp, indent=2)


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
        return f"{crawler["baseUrl"]}/{crawler["apiUrl"]}/?locale={crawler["locale"]}"

    def getApi(self, url: str) -> dict:
        response = requests.get(url)
        return response.json()

    def getWebPage(self, url: str) -> str:
        response = requests.get(url)
        print(response.request.headers)
        print(response.text)
        return response.text

    def findItemsOfInterest(self, html: str) -> ResultSet:
        soup = BeautifulSoup(html, "html5lib")
        return soup.find_all("div")

    def downloadImage(self, downloadLocation: str, imgUrl: str):
        os.makedirs(downloadLocation, exist_ok=True)
        imgData = requests.get(imgUrl).content
        imgLocation = os.path.join(downloadLocation, os.path.basename(imgUrl))
        with open(imgLocation, 'wb') as handler:
            handler.write(imgData)

    def __str__(self) -> str:
        return f"config=> {self.config}"


def main():
    startTime = time.time()
    input()
    endTime = time.time()

    print(f"Total Time:{endTime - startTime}")


if __name__ == "__main__":
    exit(main())
