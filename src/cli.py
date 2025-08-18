import argparse
from src.adapters.http.client import HttpClient
from src.adapters.http.client import get_client
import src.adapters.scrape.pfr_scraper as pfr_scraper

from typing import List
def pipeline(prospect_class: int):
    """

    :param prospect_class:
    :return:
    """

    client: HttpClient = get_client()
    draft_classes = [year for year in range(prospect_class - 5, prospect_class)]
    draft_pages: List = []
    for year in draft_classes:
        draft_pages.append(
            pfr_scraper.fetch_draft_page(year=year, client=client)
        )

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--prospect_class", type=int, required=True)
    args = argparser.parse_args()

    pipeline(args.prospect_class)
