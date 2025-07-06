'''
Calls CollegeFootballData.com API
'''

import cfbd
from cfbd.rest import ApiException

from functools import lru_cache
import logging

from typing import Dict
from typing import Any
from typing import List

import datetime as dt
import time
import pandas as pd

import config
import pos_models as Models


logger = logging.getLogger(__name__)

API_CONFIG = cfbd.Configuration(
    access_token = config.CFBD_API_KEY
)

# ---- Helper Functions ----
def _client():
    return cfbd.ApiClient(API_CONFIG)

def normalize_team_name(team_name: str) -> str:
    '''
    Helper to normalize team name to
    expected format
        *lowercase + replace spaces with underscores

    :param team_name: STRING representing college team
    :return: formatted team name
    '''
    if not team_name:
        return None

    return team_name.lower().replace(" ", "_")

# ---- Public Functions ----
@lru_cache(maxsize=128)
def search_player(name: str, *,
                  position: str = None,
                  team: str = None):
    '''
    API wrapper to fetch base attributes

    :param name: name of the player
    :param position: OPTIONAL position of the player
    :param team: OPTIONAL team of the player

    :return: Player object
    '''
    print(f"Searching... {name}, {position}, {team}")
    with _client() as client:
        api = cfbd.PlayersApi(client)
        player_hits = api.search_players(
            search_term=name,
            team=team,
            position=position
        )

    if not player_hits:
        raise ValueError(f"No matching players for {name} | {position} | {team}")

    return player_hits

def active_seasons(player_id, *,
                   team: str = None,
                   category: str = None):
    '''

    :param player_id:
    :param team:
    :param category:

    :return:
    '''
    with _client() as client:
        api = cfbd.StatsApi(client)

        res = {}

        for year in range(2010, dt.datetime.now().year + 1):
            rows = api.get_player_season_stats(year=year,
                                               category=category,
                                               team=team)

            #nothing found, skip
            if not rows:
                continue

            seen_ids = []
            for item in rows:
                #skip seen players
                if item.player_id in seen_ids:
                    continue

                if item.player_id == player_id:
                    res[year] = item.team
                    break
        return res

def get_play_stats(player_id: int, *,
                   year: int = None,
                   team: str = None,
                   ):
    '''

    :param player_id:
    :param year:
    :param team:

    :return:
    '''

    with _client() as client:
        api = cfbd.PlaysApi(client)

        team = normalize_team_name(team_name=team)

        try:
            print(player_id, year, team)
            player_id = int(player_id)

            response = api.get_play_stats(
                athlete_id=player_id,
                year=year,
                team=team,
            )

        except Exception as e:
            print(f"[ERROR] Unexpected Error\n{e}")
            return None

    return response

def list_play_types():
   '''

   :return: Prints valid play_types to stdout
   '''

   with _client() as client:
        api = cfbd.PlaysApi(client)

        try:
           response = api.get_play_types()
           for type in response:
               print(type.text)

        except Exception as e:
            print(f"[ERROR] Unexpected Error\n{e}")

        return


def get_plays(player_id, *,
              year: int = None,
              team: str = None,
              offense: str = None,
              defense: str = None,
              ):
    '''

    :param player_id:
    :param year:
    :param team:
    :param play_type:

    :return:
    '''

    team = normalize_team_name(team_name=team)

    with _client() as client:

        try:
            api = cfbd.PlaysApi(client)

            res = []
            for week in range(1, 13):
                response = api.get_plays(
                    year=year,
                    week=week,
                    team=team,
                    offense=offense,
                    defense=defense,
                )
                res.append(response)
                break

            return res

        except Exception as e:
            print(f"[ERROR] Unexpected Error\n{e}")
            return None