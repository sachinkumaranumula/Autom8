from typing import List, NotRequired, TypedDict


class ArchInfo(TypedDict):
    id: str
    title: str
    summary: str
    url: str
    thumbnail: NotRequired[str]
    categories: NotRequired[List[str]]
    products: NotRequired[List[str]]

    @staticmethod  # type: ignore
    def keys():
        return [*ArchInfo.__dict__["__annotations__"].keys()]
