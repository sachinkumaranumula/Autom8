#!/usr/bin/env python3
# python3 -m pip install -U {packages-to-install}
# Run:
# python crawler-puller.py
import argparse
import json
import time
from itertools import count
from typing import List

from img_crawler_downloader.classes import arch
from img_crawler_downloader.classes.crawler import ArchApiCrawler
from img_crawler_downloader.classes.exporter import ArchExporter


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
    # selective crawl and pull
    # crawler = ArchApiCrawler(config["crawlers"][0]["config"]["api"])
    arch_catalogs: List[arch.ArchCatalog] = []
    for crawl_config in config["crawlers"]:
        print("Started Fetching Catalog: ", crawl_config["name"])
        crawler = ArchApiCrawler(crawl_config["config"]["api"])
        arch_infos: List[arch.ArchInfo] = crawler.getArchInfos()
        arch_catalog: arch.ArchCatalog = {
            "name": crawl_config["name"],
            "archs": arch_infos,
            "count": len(arch_infos),
        }
        arch_catalogs.append(arch_catalog)
        print("Finished Fetching Catalog: ", crawl_config["name"])
    exporter = ArchExporter(config["exporter"])
    exporter.saveArchInfosAsCSV(arch_catalogs)
    exporter.saveArchInfosAsJson(arch_catalogs)
    # exporter.downloadThumbnails(arch_catalogs)


def main():
    startTime = time.time()
    config = get_config()
    crawl_and_pull(config)
    endTime = time.time()
    print(f"Total Time:{endTime - startTime}")


if __name__ == "__main__":
    exit(main())
