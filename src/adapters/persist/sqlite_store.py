'''

'''

import sqlite3
import json
import dataclasses

import os
import logging
from typing import Iterable, Iterator, Optional

from src.config import DATA_DIR
from src.core.models import Player
from src.core.models import make_player

logger = logging.getLogger(__name__)

_DB_PATH = os.path.join(DATA_DIR, "db", "prospects.db")


_SQL_SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    position   TEXT NOT NULL,
    age        INTEGER,
    height     INTEGER,
    weight     INTEGER,
    college    TEXT,
    stats_link TEXT,
    stats_json TEXT,
    UNIQUE(name, college, position)
);
"""
_UPSERT_SQL = """
INSERT INTO players (name, position, age, height, weight, college, stats_link, stats_json)
VALUES (:name, :position, :age, :height, :weight, :college, :stats_link, :stats_json)
ON CONFLICT(name, college, position) DO UPDATE SET
  age        = excluded.age,
  height     = excluded.height,
  weight     = excluded.weight,
  stats_link = excluded.stats_link,
  stats_json = excluded.stats_json
"""

_SELECT_ONE_SQL = """
SELECT name, position, age, height, weight, college, stats_link, stats_json
FROM players
WHERE name = ? AND college = ? AND position = ?
"""

_SELECT_BY_POS_SQL = """
SELECT name, position, age, height, weight, college, stats_link, stats_json
FROM players
WHERE position = ?
ORDER BY name COLLATE NOCASE
"""

class ProspectStorage:
    def __init__(self, db_path: str = None) -> None:

        self._db_path = db_path or _DB_PATH
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)

        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._db_init()

        self._conn.execute("PRAGMA synchronous = NORMAL;")

    def __enter__(self) -> "ProspectStorage":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def _db_init(self) -> None:
        self._conn.executescript(_SQL_SCHEMA)

    def _player_to_row(self, player: Player) -> dict:
        '''
        Helper function to convert a Player object into a dictionary, including the
        positional stats

        :param player:
        :return:
        '''
        player_dict = {
            "name": getattr(player, "name", None),
            "position": getattr(player, "position", None),
            "age": getattr(player, "age", None),
            "height": getattr(player, "height", None),
            "weight": getattr(player, "weight", None),
            "college": getattr(player, "college", None),
            "stats_link": getattr(player, "stats_link", None),
            "stats_json": json.loads(getattr(player, "stats_json", "{}"))
        }

        # collection positional stats in a json file
        positional_stats = {
            key: value for key, value in dataclasses.asdict(player).items()
            if key not in player_dict and value is not None
        }
        # that was a hefty piece of python

        if positional_stats:
            player_dict['stats_json'] = json.dumps(positional_stats, ensure_ascii=False)

        return player_dict

    def _row_to_player(self, row: sqlite3.Row) -> Optional[Player]:
        '''

        :param row:
        :return:
        '''
        if row is None:
            return None

        player = make_player(
            position=row["position"],
            name=row["name"],
            age=row["age"],
            height=row["height"],
            weight=row["weight"],
            college=row["college"],
            stats_link=row["stats_link"],
        )

        try:
            extra = json.loads(row["stats_json"]) if row["stats_json"] else {}
            if isinstance(extra, dict):
                for key, value in extra.items():
                    if key not in {"name", "position", "age", "height", "weight", "college", "stats_link"}:
                        try:
                            setattr(player, key, value)
                        except Exception as e:
                            logger.warning(f"Skipped {key} = {value} for {player.name}: {e}")
                            pass
        except Exception as e:
            logger.debug(f"Failed to load stats_json for {row['name']}: {e}")

        return player

    def update_players(self, players: Iterable[Player]) -> int:
        '''

        :param players:
        :return:
        '''
        rows = [self._player_to_row(player) for player in players]
        if not rows:
            return 0

        with self._conn:
            self._conn.executemany(_UPSERT_SQL, rows)
        return len(rows)

    def get_player(self, *,
                   name: str,
                   college: str,
                   position: str) -> Optional[Player]:
        '''

        :param name:
        :param college:
        :param position:
        :return:
        '''
        cursor = self._conn.execute(_SELECT_ONE_SQL, (name, college, position))
        row = cursor.fetchone()
        return self._row_to_player(row) if row else None

    def list_by_position(self, pos: str) -> Iterator[Player]:
        '''

        :param pos:
        :return:
        '''

        cursor = self._conn.execute(_SELECT_BY_POS_SQL, (pos,))
        for row in cursor:
            player = self._row_to_player(row=row)
            if player is not None:
                yield player

    def close(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass
