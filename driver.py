'''
Uses all the modules together to build the main pipeline
'''

import argparse
import sys
import time
import traceback

from scrape.http import get_client
from scrape import pfr_scraper
from parse import pfr_parser
from db import sqlite as db
from pos_models import Player


def scrape_year(year: int):
    '''
    Fetch draft year and return Player objects

    :param year : Draft year to fetch + parse
    :return     : Dictionary mapping {Position: List[Player]
    '''

    #define HttpClient + SQL connection to DB
    client = get_client()
    connection = db.sql_get_connection()

    start_stamp = time.time()

    #fetch the HTML
    html = pfr_scraper.fetch_prospects_page(year=year, client=client)

    #parse the HTML
    players = pfr_parser.parse_prospect_page(html=html)

    print(players.keys())
    #get the each players positional stats
    for pos, player_stubs in players.items():
        filled_players = []

        for player in player_stubs:
            print(f"Processing {player.name}...")
            #skip players who dont have a college stats link
            if not player.stats_link:
                continue

            try:
                html = pfr_scraper.fetch_player_page(href=player.stats_link, client=client)
                pfr_parser.parse_player_page(html=html, player=player)
                filled_players.append(player)
            except Exception as e:
                print(f"\t[WARNING] Failed {player.name}: {e}"
                      f"\t\t{traceback.format_exc()}")

        db.sql_update_players(filled_players, connection=connection)
        print(f"\t[INFO] Inserted {len(filled_players)} players to DB")

    #close DB connection after all positions have been iterated
    connection.close()
    print(f"[INFO] Finished in {(time.time() - start_stamp) / 60 :.3f} minutes")

    return players

def main():
    scrape_year(year=2025)

if __name__ == "__main__":
    main()