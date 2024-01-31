from typing import List, TypedDict

from classes.config import Api, Config, Crawler

# TODO: FINISH JOB CONFIG


class Job(TypedDict):
    name: str
    description: str
    tags: List[str]
    crawlers: List[Crawler]
    downloader: str


class Crawler(TypedDict):
    name: str
    config: Config


class Config(TypedDict):
    api: Api


class Api(TypedDict):
    request: str
    response: str
