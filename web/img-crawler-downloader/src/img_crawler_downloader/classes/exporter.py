import csv
import json
import os.path
from typing import List

import requests
from img_crawler_downloader.classes.arch_info import ArchInfo

DOWNLOAD_SEGMENT_IMAGES = "images"
DOWNLOAD_SEGMENT_COLLECTION = "collection"


class ArchExporter:
    def __init__(self, config: dict) -> None:
        self.config = config

    def downloadThumbnails(self, arch_infos: list) -> None:
        for arch_info in arch_infos:
            self.downloadImage(arch_info["thumbnail"])

    def downloadImage(self, imgUrl: str) -> None:
        imgData = requests.get(imgUrl).content
        imgLocation = os.path.join(
            self.downloadLocation(DOWNLOAD_SEGMENT_IMAGES), os.path.basename(imgUrl)
        )
        with open(imgLocation, "wb") as handler:
            handler.write(imgData)

    def downloadLocation(self, segment) -> str:
        downloadLocation = self.config["downloader"]["location"]
        downloadPath = os.path.join(downloadLocation, segment)
        os.makedirs(downloadPath, exist_ok=True)
        return downloadPath

    def saveArchInfosAsCSV(self, arch_infos: List[ArchInfo]) -> None:
        archsLocation = os.path.join(
            self.downloadLocation(DOWNLOAD_SEGMENT_COLLECTION), "archs.csv"
        )
        with open(archsLocation, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=ArchInfo.keys())
            writer.writeheader()
            writer.writerows(arch_infos)

    def saveArchInfosAsJson(self, arch_infos: list) -> None:
        arch_json: dict = {"archs": arch_infos, "count": len(arch_infos)}
        archsLocation = os.path.join(
            self.downloadLocation(DOWNLOAD_SEGMENT_COLLECTION), "archs.json"
        )
        with open(archsLocation, "w") as jsonfile:
            jsonfile.write(json.dumps(arch_json, indent=1))
