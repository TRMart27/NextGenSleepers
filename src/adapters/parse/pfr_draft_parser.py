from src import config
import src.adapters.parse.pfr_parser as Parser
from src.adapters.scrape.pfr_draft_scraper import stat_path
import src.core.models as models

from collections import defaultdict

from typing import Dict, List

import os
import logging

logger = logging.getLogger(__name__)


def parse_draft_pages(
    pages: Dict[int, str],
) -> Dict[int, Dict[str, List[models.NFLDraftee]]]:
    """

    :param pages:

    :return:
    """

    drafted_players = defaultdict(dict)

    for year, html in pages.items():
        drafted_players[year] = Parser.parse_draft_page(html=html)

    if len(drafted_players) == 0:
        logger.warning("Drafted Players is empty! <parse_draft_pages>")

    return drafted_players


def parse_draftee_stat_pages(
    drafted_players: Dict[int, Dict[str, List[models.NFLDraftee]]],
) -> None:
    """Enriches NFLDraftee stats from cached html files"""

    if len(drafted_players) == 0:
        logger.debug(" No players drafted! <parse_draftee_stat_pages>")
        return

    for year, position_list in drafted_players.items():
        for position, position_players in position_list.items():
            for athlete in position_players:
                name = getattr(athlete.player, "name", None) or getattr(
                    athlete, "name", None
                )
                filepath = os.path.join(
                    config.CACHE_DIR, stat_path(year=year, position=position, name=name)
                )

                # skip if not cached
                if not os.path.exists(filepath):
                    logger.info(f"Cache missing html for {name}")
                    continue

                # load from cache
                try:
                    with open(filepath, "r", encoding="utf-8") as file_ref:
                        html = file_ref.read()
                except Exception as e:
                    logger.debug(f"Unexpected error while reading: {e}")
                    continue

                if not html:
                    logger.warning(f"Empty HTML from cache for {name}")
                    continue
                # enrich profile     inplace
                Parser.parse_player_page(html=html, player=athlete.player)

    return None
