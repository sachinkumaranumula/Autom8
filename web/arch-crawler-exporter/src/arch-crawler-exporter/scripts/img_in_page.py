import re
import time

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "3600",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
}


def img_in_page():
    url = "https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/develop-advanced-generative-ai-chatbots-by-using-rag-and-react-prompting.html?did=pg_card&trk=pg_card"
    req = requests.get(url, HEADERS)
    soup = BeautifulSoup(req.content, "html.parser")
    tag = soup.find("img", alt=re.compile("^.+$"))
    return tag["src"]  # type: ignore


def main():
    startTime = time.time()
    img_in_page()
    endTime = time.time()
    print(f"Total Time:{endTime - startTime}")


if __name__ == "__main__":
    exit(main())
