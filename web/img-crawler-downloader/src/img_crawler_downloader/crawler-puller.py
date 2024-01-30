#!/usr/bin/env python3
# python3 -m pip install -U {packages-to-install}
# Run:
# python crawler-puller.py
import argparse
import json
import time

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
    crawler = ArchApiCrawler(config["provider"]["azure"]["crawler"]["api"])
    exporter = ArchExporter(config)
    arch_infos = crawler.getArchInfos()
    exporter.saveArchInfosAsCSV(arch_infos)
    exporter.saveArchInfosAsJson(arch_infos)
    # exporter.downloadThumbnails(arch_infos)


def main():
    startTime = time.time()
    config = get_config()
    crawl_and_pull(config)
    endTime = time.time()
    print(f"Total Time:{endTime - startTime}")


if __name__ == "__main__":
    exit(main())
