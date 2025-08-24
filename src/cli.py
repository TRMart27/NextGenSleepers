"""
command line interface to glue everything together

USAGE   :: python3 ./cli.py --prospect_class <INT> --do_caching <bool>
EXAMPLE :: python3 /cli.py --prospect_class 2025 --do_caching True

    - Checks local cache for HTML files
    - fetches necessary webpages
    - caches HTML if flag is set
    - parsers pages for player data
"""

# --- scrapers ---
from src.adapters.http.client import get_client
import src.adapters.scrape.pfr_draft_scraper as pfr_draft_scraper
import src.adapters.scrape.pfr_scraper as pfr_scraper

# --- parsers ---
import src.adapters.parse.pfr_parser as pfr_parser
import src.adapters.parse.pfr_draft_parser as pfr_draft_parser


# --- storage imports ---
import src.adapters.persist.cache_store as cache
import src.adapters.persist.json_store as json
from src.adapters.persist.sqlite_store import ProspectStorage
from src.config import CACHE_DIR

# --- python imports ---
from typing import List, Dict
import argparse
import logging
import os
import time
from dataclasses import asdict

logger = logging.getLogger(__name__)
logging.basicConfig(filename="cli.log", level=logging.INFO)
# create a single global shared client
_client = get_client()


def _sanitize_player_name(name: str) -> str:
    return name.replace(" ", "")


def _player_stat_path(name: str, position: str) -> str:
    return os.path.join(CACHE_DIR, "data", "raw", "stat_pages", f"{_sanitize_player_name(name)}_{position}.html")


def _enrich_draftee_profiles(draftees, cache_flag: bool):
    start_time = time.monotonic()
    for year, all_players in draftees.items():
        for position in all_players.keys():
            for athlete in all_players[position]:
                if athlete.player.stats_link is None:
                    logger.info(f"Skipping {athlete.player.name}, missing or invalid stats_link")
                    continue
                save_path = _player_stat_path(athlete.player.name, position)
                if os.path.exists(save_path):
                    html = cache.load_html(save_path)
                else:
                    logger.info(f"Cache miss for {athlete.player.name} - fetching from {athlete.player.stats_link}")
                    html = pfr_scraper.fetch_player_page(athlete.player.stats_link, client=_client)
                    if cache_flag:
                        cache.cache_html(save_path, html)
                #parse the page, modify player in place
                pfr_parser.parse_player_page(html, athlete.player)
                pfr_parser.parse_height_weight(html, athlete)

            filepath = json.position_path(year, position)
            logger.info(f"[INFO] Saving {year} - {position} to {filepath}")
            players = [asdict(p) for p in all_players[position]]
            json.write_json(filepath, json.prepare_payload(year, position, players))

        elapsed_time = time.monotonic() - start_time
        logger.info(f"[INFO] Finished {year} in {elapsed_time/60:.2f} minutes")

def _enrich_prospects_profile(prospects, cache_flag) -> None:
    """

    :param prospects:
    :return:
    """
    prospects_db = ProspectStorage()
    for position, players in prospects.items():
        time_start = time.monotonic()
        for player in players:
            if player.stats_link is None:
                logger.info(f"Skipping {player.name}, missing or invalid stats_link")
                continue
            save_path = _player_stat_path(player.name, position)
            if os.path.exists(save_path):
                html = cache.load_html(save_path)
            else:
                logger.info(f"Cache miss for {player.name} - fetching from {player.stats_link}")
                html = pfr_scraper.fetch_player_page(player.stats_link, client=_client)
                cache.cache_html(save_path, html)
            pfr_parser.parse_player_page(html, player)
            print(player)
        if prospects_db.update_players(players) == 0:
            logger.debug(f"No players updated for {position}")

        elapsed_time = time.monotonic() - time_start
        logger.info(f"[INFO] Finished {position} in {elapsed_time/60:.2f} minutes")

def _enhance_qb_profiles() -> None:
    """

    :return:
    """
    pass

def pipeline(prospect_class: int):
    """

    :param prospect_class:
    :return:
    """
    year_start = prospect_class - 5

    draft_pages = pfr_draft_scraper.fetch_draft_pages(year_start, prospect_class - 1, client=_client)
    draftees = pfr_draft_parser.parse_draft_pages(draft_pages)
    _enrich_draftee_profiles(draftees)

    prospect_html = pfr_scraper.fetch_prospects_page(2025, client=_client)
    prospects = pfr_parser.parse_prospect_page(prospect_html)
    _enrich_prospects_profile(prospects)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--prospect_class", type=int, required=True)
    argparser.add_argument("--do_caching", type=bool, required=False, default=True)

    args = argparser.parse_args()
    pipeline(args.prospect_class)
