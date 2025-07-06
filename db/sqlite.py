'''
SQLite to persist player data to avoid Http calls
'''

import sqlite3
import json
import pandas as pd

from pathlib import Path
from typing import List

import dataclasses
from pos_models import Player
import config

_DATA_PATH = config.DATA_DIR / "prospects.db"

_SQL_SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    position   TEXT NOT NULL,
    age        INTEGER,
    height     INTEGER,
    weight     INTEGER,
    college    TEXT,
    stats_linK TEXT,
    stats_json TEXT,
    UNIQUE(name, college, position)
);
"""


# ---- Helper Functions ----
def db_init(path: str = _DATA_PATH) -> None:
    '''
    Initializes the DB file + schmea

    :param path  : path to the sqlite database file
    :return      : Nothing
    '''
    connection = sqlite3.connect(path)
    try:
        connection.executescript(_SQL_SCHEMA)
    finally:
        connection.close()

    return

def sql_get_connection(path: str = _DATA_PATH) -> sqlite3.Connection:
    '''
    Returns a connection object to the sqlite database

    :param path  : path to sqlite database
    :return      : sqlite connection
    '''
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row

    return connection

#initialize the DB
db_init()

# ---- DB Helper Functions ----
def _player_to_row(player: Player) -> dict:
    '''
    Helper function to convert a Player object into a dictionary, including the
    positional stats

    :param player:
    :return:
    '''
    player_dict = {
        "name": player.name,
        "position": player.position,
        "age": player.age,
        "height": player.height,
        "weight": player.weight,
        "college": player.college,
        "stats_link": player.stats_link,
        "stats_json": json.dumps(getattr(player, "stats_json", {}))
    }


    #collection positional stats in a json file
    positional_stats = {
        key: value for key, value in dataclasses.asdict(player).items()
        if key not in player_dict and value is not None
    }
    #that was a hefty piece of python

    if positional_stats:
        player_dict['stats_json'] = json.dumps(positional_stats)

    return player_dict


# ---- DB Writing Helper ----
def sql_update_players(players: List[Player],
                   *, connection: sqlite3.Connection = None) -> None:
    '''
    Insert / update player objects
    :param players:
    :param connection:
    :return:
    '''

    do_close = False
    if connection is None:
        connection = sql_get_connection()
        do_close = True

    sql_query = (
        "INSERT INTO players (name, position, age, height, weight, college, stats_link, stats_json)"
        "VALUES (:name, :position, :age, :height, :weight, :college, :stats_link, :stats_json)"
        "ON CONFLICT (name, college, position) DO UPDATE SET\n"
        "  age        = excluded.age,\n"
        "  height     = excluded.height,\n "
        "  weight     = excluded.weight,\n"
        "  stats_link = excluded.stats_link,\n"
        "  stats_json = excluded.stats_json;"
    )
    rows = [_player_to_row(player) for player in players]

    with connection:
        connection.executemany(sql_query, rows)

    if do_close:
        connection.close()

    return


# ---- DB Reading Helpers ----
def _expand_json(df: pd.DataFrame) -> pd.DataFrame:
    '''

    :param df:
    :return:
    '''
    if not df.empty:
        filled = []
        for val in df['stats_json']:
            if val:
                filled.append(json.loads(val))
            else:
                filled.append({})
        expanded_json = pd.json_normalize(filled)

        df = df.drop(columns=['stats_json']).reset_index(drop=True)
        df = pd.concat([df, expanded_json], axis=1)
        return df

def sql_search_players(
        *, name: str = None, position: str = None, college: str = None,
        connection: sqlite3.Connection = None) -> pd.DataFrame:
    '''

    *
    :param name:
    :param position:
    :param college:
    :param connection:
    :return:
    '''

    #make a connection if needed
    do_close = False
    if connection is None:
        connection = sql_get_connection()
        do_close = True

    sql_query = "SELECT * FROM players"
    params = list()

    #build SQL query
    if name:
        sql_query += " WHERE name = ?"
        params.append(name)
    if position:
        sql_query += " WHERE position = ?"
        params.append(position)

    if college:
        sql_query += " WHERE college = ?"
        params.append(college)


    #store result in df
    df = pd.read_sql(sql_query, connection, params=params)

    #if there was a result, expand the json
    df = _expand_json(df=df)

    if do_close:
        connection.close()

    return df

