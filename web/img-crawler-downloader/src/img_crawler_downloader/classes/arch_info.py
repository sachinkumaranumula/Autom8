from typing import List, TypedDict


class ArchInfo(TypedDict):
    title: str
    summary: str
    thumbnail: str
    url: str
    categories: List[str]
    products: List[str]

    @staticmethod  # type: ignore
    def keys():
        return [*ArchInfo.__dict__["__annotations__"].keys()]
