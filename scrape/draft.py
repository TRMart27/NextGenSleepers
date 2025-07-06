'''
Wraps network calls to fetch previous draft pages from PFR
'''


import config
import scrape.http as http
import scrape.pfr as Scraper
import pos_models as Models
import db.json as Store

from typing import Dict
from typing import List

import os


#---- Helper Functions ----
def _cache_html(html: str, filepath: str):

    #ensure directories exist before writing
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    try:
        with open(filepath, "w", encoding="utf-8") as file_ref:
            file_ref.write(html)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return

    print(f"[INFO] Cached html at {filepath}")
    return


def _load_html(path: str) -> str:

    if not os.path.exists(path):
        print(f"[ERROR] File not found: {path}")
        return None

    try:
        with open(path, "r", encoding="utf-8") as file_ref:
            return file_ref.read()
    except Exception as e:
        print(f"[ERROR] Unexpected Erorr: {e}")
        return None


def stat_path(year: int, position: str) -> str:
    ''' Builds the relative filepath to the stats HTML'''

    return os.path.join("stat_pages", str(year), f"{position}.html")


def _page_path(year: int) -> str:
    ''' Builds the relative filepath to the page HTML '''

    return os.path.join("pages", f"{year}.html")



# ---- Public Wrappers ----
def fetch_draft_pages(year_start: int, year_end: int,
                      *, client: http.HttpClient) -> Dict[int, str]:
    '''
    Calls fetch_draft_page for years between start and end
    :param year_start:
    :param year_end:
    :param client:

    :return:
    '''

    out: Dict[int, str] = {}
    for year in range(year_start, year_end):
        #build path
        save_path = os.path.join(config.draft_path, _page_path(year))

        #check
        if os.path.exists(save_path):
            html = _load_html(path=save_path)
        else:
            #scrape
            html = Scraper.fetch_draft_page(year=year, client=client)
            if html is None:
                print(f'[WARNING] Failed to fetch draft from {year}')
                continue

            #persist
            _cache_html(html=html, filepath=save_path)
        #store
        out[year] = html

    return out

def fetch_drafted_profile_html(drafted_players: Dict[int, Dict[str, List[Models.NFLDraftee]]],
                           *, client: http.HttpClient)\
        -> Dict[int, Dict[str, List[str]]]:
    '''
    Wraps fetch_player_page
    :param pages:

    :return:
    '''
    html_all: Dict[int, Dict[str, List[str]]] = {}

    for year, position_list in drafted_players.items():
        html_all[year] = {}

        for position, position_players in position_list.items():
            stats_htmls: List[str] = []

            for athlete in position_players:
                #skip missing links
                if athlete.player.stats_link is None:
                    continue

                #build path
                save_path = os.path.join(config.CACHE_DIR, stat_path(year, position))

                #load if cached
                if os.path.exists(save_path):
                    html = _load_html(path=save_path)
                else:
                   html = Scraper.fetch_player_page(href=athlete.player.stats_link, client=client)
                   if html is None:
                       print(f'[WARNING] Failed to fetch page for {athlete.player}')
                       continue
                   _cache_html(html=html, filepath=save_path)

                #append
                stats_htmls.append(html)
            #store
            html_all[year][position] = stats_htmls

    return html_all




