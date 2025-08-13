import config
import adapters.parse.pfr_parser as Parser
from adapters.scrape.draft import stat_path
import core.models as Models

from collections import defaultdict

from typing import Dict
from typing import List

import os

def parse_draft_pages(pages: Dict[int, str])\
    -> Dict[int, Dict[str, List[Models.NFLDraftee]]]:
    '''

    :param pages:

    :return:
    '''

    drafted_players = defaultdict(dict)

    for year, html in pages.items():
        drafted_players[year] = Parser.parse_draft_page(html=html)

    if len(drafted_players) == 0:
        print("[WARNING] Drafted Players is empty! <parse_draft_pages>")

    return drafted_players


def parse_draftee_stat_pages(drafted_players: Dict[int, Dict[str, List[Models.NFLDraftee]]]) -> None:
    ''' Enriches NFLDraftee stats from cached html files'''

    if len(drafted_players) == 0:
        print("[ERROR] No players drafted! <parse_draftee_stat_pages>")
        return

    for year, position_list in drafted_players.items():
        for position, position_players in position_list.items():
            for athlete in position_players:
                filepath = os.path.join(config.CACHE_DIR, stat_path(year=year, position=position, name=athlete.name.name))

                #skip if not cached
                if not os.path.exists(filepath):
                    print(f"[INFO] Cache missing html for {athlete.player.name}")
                    continue

                #load from cache
                try:
                    with open(filepath, "r", encoding="utf-8") as file_ref:
                        html = file_ref.read()
                except Exception as e:
                    print(f"[ERROR] Unexpected error while reading: {e}")
                    continue

                #enrich profile     inplace
                Parser.parse_player_page(html=html, player=athlete.player)

    return None