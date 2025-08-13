'''
Wraps network calls to fetch previous draft pages from PFR
'''

import config
import adapters.http.client as http
import adapters.scrape.pfr_scraper as Scraper
import core.models as Models

from typing import Dict
from typing import List

import os
import logging

logger = logging.getLogger(__name__)

#---- Helper Functions ----
def _cache_html(html: str, filepath: str):

    #ensure directories exist before writing
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    try:
        with open(filepath, "w", encoding="utf-8") as file_ref:
            file_ref.write(html)
    except Exception as e:
        logger.debug(f" Unexpected error: {e}")
        return

    logger.info(f"Cached html at {filepath}")
    return


def _load_html(path: str) -> str:

    if not os.path.exists(path):
        logger.debug(f"File not found: {path}")
        return None

    try:
        with open(path, "r", encoding="utf-8") as file_ref:
            return file_ref.read()
    except Exception as e:
        logger.debug(f"Unexpected Erorr: {e}")
        return None

def clean_name(name: str) -> str:
    ''' Ensure the player name is safe for path building
    strips whitespaces'''

    if not name:
        logger.debug('Invalid player name <normalize_name>')
        raise ValueError("Invalid player name <normalize_name>")

    return name.replace(" ", "")

def stat_path(year: int, position: str, name: str) -> str:
    ''' Builds the relative filepath to the stats HTML'''

    name = clean_name(name=name)
    return os.path.join("stat_pages", str(year), position, f"{name}.html")


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
    for year in range(year_start, year_end + 1):
        #build path
        save_path = os.path.join(config.CACHE_DIR, _page_path(year))

        #check
        html = _load_html if os.path.exists(save_path) else None
        if html is None:
            html = Scraper.fetch_draft_page(year=year, client=client)
            if html is None:
                logger.warning(f"Failed to fetch draft page for year {year}")
                continue
            _cache_html(html=html, filepath=save_path)
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
                if athlete.stats_link is None:
                    continue

                #build path
                save_path = os.path.join(config.CACHE_DIR, stat_path(year, position, athlete.name.name))

                #load if cached
                html = _load_html if os.path.exists(save_path) else None
                if html is None:
                    html = Scraper.fetch_player_page(href=athlete.stats_link, client=client)
                    if html is None:
                        logger.warning(f"Failed to fetch page for {athlete.player}")
                    #persist
                    _cache_html(html=html, filepath=save_path)

                #append
                stats_htmls.append(html)
            #store
            html_all[year][position] = stats_htmls

    return html_all