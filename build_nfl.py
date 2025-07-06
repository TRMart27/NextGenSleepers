import config
from bs4 import BeautifulSoup
import scrape.http as http
import scrape.pfr as Scraper
import parse.pfr_parser as Parser
import pos_models as Models
import db.json as StoreJSON

from typing import Dict
from typing import List
from collections import defaultdict
from dataclasses import asdict
from tqdm import tqdm

import pandas as pd

import time
import json
from datetime import datetime
import os
import re

#fetch draft html -> pft_scraper.fetch_draft_page
#parse html = pfr_parser.parse_draft_page

def load_html(filepath: str) -> str:
    '''
    loads the specified HTML page stored at <filepath>
    :param filepath:

    :return:
    '''
    try:
        with open(filepath, "r", encoding="utf-8") as file_ref:
            html = file_ref.read()
            return html
    except Exception as e:
        print(f"An Unexpected Error has Occured: {e}")

def main():
    client = http.get_client()

    current_year = datetime.now().year
    year_range = (current_year - 5, current_year)

    all_htmls = {}
    for year in range(*year_range):
        path = os.path.join(config.CACHE_DIR, "pages", f"{year}.html")
        if os.path.exists(path):
            html = load_html(path)
        else:
            html = Scraper.fetch_draft_page(year=year, client=client)
        all_htmls[year] = html

    draftees = defaultdict(dict)
    for year, html in all_htmls.items():
        draftees[year] = Parser.parse_draft_page(html=html)

    time_stamp = time.time()

    for year, all_players in draftees.items():
        for position in all_players.keys():
            for player in tqdm(all_players[position], total=len(all_players[position])):
                if player.player.stats_link is None:
                    continue
                html = Scraper.fetch_player_page(href=player.player.stats_link, client=client)
                player.player = Parser.parse_player_page(html=html, player=player.player)
                Parser.parse_height_weight(html=html, athlete=player)
                print(player)
            StoreJSON.send_to_json(all_players[position], filepath=f"{config.CACHE_DIR}/draft_{year}_{position}.json")

    elasped = time.time() - time_stamp
    print(f"Finished in {elasped / 60:.2f} minutes")

if __name__ == "__main__":
    main()
