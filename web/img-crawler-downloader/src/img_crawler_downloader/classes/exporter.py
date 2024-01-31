import csv
import json
import os.path
from typing import List

import requests
from img_crawler_downloader.classes.arch import ArchCatalog, ArchInfo

DOWNLOAD_SEGMENT_IMAGES = "images"
DOWNLOAD_SEGMENT_COLLECTION = "collection"


class ArchExporter:
    def __init__(self, config: dict) -> None:
        self.config = config

    def downloadThumbnails(self, arch_catalogs: List[ArchCatalog]) -> None:
        for arch_catalog in arch_catalogs:
            for arch_info in arch_catalog["archs"]:
                if "thumbnail" in arch_info:
                    self.downloadImage(arch_info["thumbnail"])

    def downloadImage(self, imgUrl: str) -> None:
        imgData = requests.get(imgUrl).content
        imgLocation = os.path.join(
            self.downloadLocation(DOWNLOAD_SEGMENT_IMAGES), os.path.basename(imgUrl)
        )
        with open(imgLocation, "wb") as handler:
            handler.write(imgData)

    def downloadLocation(self, segment) -> str:
        downloadLocation = self.config["location"]
        downloadPath = os.path.join(downloadLocation, segment)
        os.makedirs(downloadPath, exist_ok=True)
        return downloadPath

    def saveArchInfosAsCSV(self, arch_catalogs: List[ArchCatalog]) -> None:
        for arch_catalog in arch_catalogs:
            archsLocation = os.path.join(
                self.downloadLocation(DOWNLOAD_SEGMENT_COLLECTION),
                f"{arch_catalog['name']}.csv",
            )
            with open(archsLocation, "w") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=ArchInfo.keys())
                writer.writeheader()
                writer.writerows(arch_catalog["archs"])

    def saveArchInfosAsJson(self, arch_catalogs: List[ArchCatalog]) -> None:
        for arch_catalog in arch_catalogs:
            archsLocation = os.path.join(
                self.downloadLocation(DOWNLOAD_SEGMENT_COLLECTION),
                f"{arch_catalog['name']}.json",
            )
            arch_json: dict = {
                "archs": arch_catalog["archs"],
                "count": arch_catalog["count"],
            }
            with open(archsLocation, "w") as jsonfile:
                jsonfile.write(json.dumps(arch_json, indent=1))
