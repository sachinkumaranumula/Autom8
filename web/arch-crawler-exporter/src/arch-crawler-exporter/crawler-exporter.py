#!/usr/bin/env python3
# python3 -m pip install -U {packages-to-install}
# Run:
# python crawler-exporter.py
import argparse
import json
import time
from typing import List

from classes import arch
from classes.crawler import ArchApiCrawler, ArchWebCrawler
from classes.exporter import ArchExporter


def __getConfig() -> dict:
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


def __crawlAndExport(config: dict):
    arch_catalogs: List[arch.ArchCatalog] = []
    for crawl_group in config["crawlerGroups"]:
        arch_infos: List[arch.ArchInfo] = []
        for crawl_config in crawl_group["crawlers"]:
            arch_infos.extend(__crawlArchs(crawl_config))
        arch_catalogs.append(__makeArchCatalog(crawl_group, arch_infos))
    __exportCatalogs(config, arch_catalogs)


def __exportCatalogs(config, arch_catalogs):
    exporter = ArchExporter(config["exporter"])
    exporter.saveArchInfosAsCSV(arch_catalogs)
    exporter.saveArchInfosAsJson(arch_catalogs)
    # exporter.downloadThumbnails(arch_catalogs)


def __makeArchCatalog(crawl_group_config, arch_infos) -> arch.ArchCatalog:
    arch_catalog: arch.ArchCatalog = {
        "name": crawl_group_config["name"],
        "archs": arch_infos,
        "count": len(arch_infos),
    }
    return arch_catalog


def __crawlArchs(crawl_config) -> List[arch.ArchInfo]:
    print("Started Fetching:", crawl_config["name"])
    api_crawler = ArchApiCrawler(crawl_config["config"]["api"])
    arch_infos: List[arch.ArchInfo] = api_crawler.getArchInfos()
    __webCrawlIfNecessary(
        crawl_config, arch_infos, crawl_config["config"]["api"]["request"]["baseUrl"]
    )
    print("Finished Fetching:", crawl_config["name"])
    return arch_infos


def __webCrawlIfNecessary(crawl_config, arch_infos, baseUrl) -> None:
    if "web" in crawl_config["config"]:
        web_crawler = ArchWebCrawler(crawl_config["config"]["web"])
        web_crawler.enrichWithSelectors(arch_infos)


def main():
    startTime = time.time()
    config = __getConfig()
    __crawlAndExport(config)
    endTime = time.time()
    print(f"Total Time:{endTime - startTime}")


if __name__ == "__main__":
    exit(main())
