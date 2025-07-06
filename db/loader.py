#my stuff
import config
import pos_models as Models
import db.sqlite as StoreSQL
import db.json as StoreJSON

from typing import Dict
from typing import List
from collections import defaultdict

import pandas as pd

import os

def _strip_player_prefixs(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Internal helper to strip the "player.*" prefix from
    column names after loading json file

    :param df: draftee DataFrame

    :return: cleaned dataframe with normalized column names
    (EXAMPLE :: player.height -> height)
    '''
    #iter columns,
    #   if it starts with "player."
    #       #handle it

    df = df.rename(columns=\
                        lambda x: x.replace("player.", "")\
                        if x.startswith("player.")\
                        else x,\
    )

    return df


def get_draftees_by_position(position: str) -> pd.DataFrame:
    '''
    JSON Wrapper to load draftees by position

    :param position:
    :param year

    :return:
    '''

    parent_dir = os.path.join(config.CACHE_DIR, r"profiles")
    if not os.path.exists(parent_dir):
        raise FileExistsError(f"[ERROR] Directory {parent_dir} does not exist!")

    # uppercase for sanity
    position = position.upper()
    df_all       = pd.DataFrame()
    for child_dir in os.listdir(parent_dir):
        path = os.path.join(parent_dir, child_dir)

        if not os.path.exists(path):
            raise FileExistsError(f"[ERROR] Directory {path} does not exist!")

        for file in os.listdir(path):
            #is this the right position + a json?
            if file.startswith(position) and file.endswith(".json"):
                #load the file
                df = StoreJSON.load_json(
                    filepath=os.path.join(path, file)
                )
                #concat the frames together
                df_all = pd.concat([df_all, df], ignore_index=True)
                break # - found the file, you can stop now bro

    return _strip_player_prefixs(df=df_all)


def load_draftees_by_year(year: int) -> List[pd.DataFrame]:

    '''

    :param year:

    :return:
    '''
    dir_path = os.path.join(config.CACHE_DIR, r"profiles", f"{year}")
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f'[ERROR] Directory does not exist: {dir_path}')

    players: List = [] #list of DataFrames
    for position in Models.POSITION_CLASS_MAP.keys():
        pos_df = get_draftees_by_position(position=position, year=year)
        players.append(pos_df)

    return players


def get_prospects_by_position(position: str) -> pd.DataFrame:
    '''
    SQL Query wrapper to grab all prospects by position
    :param position:

    :return:
    '''
    prospects = StoreSQL.sql_search_players(position=position)
    prospects = prospects.drop(columns=['id', 'stats_linK'], axis=1)

    return prospects


def load_prospects() -> Dict[str, List]:
    '''
    Returns a dictionary of prospects, where position is the key to a list of prospects

    :return:
    '''
    all_prospects: Dict = defaultdict(list)
    for position in Models.POSITION_CLASS_MAP.keys():

        pos_prospects: List = []
        df = get_prospects_by_position(position=position)
        df_dict = df.to_dict(orient='records')

        for profile in df_dict:
            # get proper class
            prospect = Models.get_position_class(position=position,
                                                 **profile,
                                                 stats_link=stats_link
                                                 )
            pos_prospects.append(prospect)

        all_prospects[position] = pos_prospects

    return all_prospects
