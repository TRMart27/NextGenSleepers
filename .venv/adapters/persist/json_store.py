'''


'''

import dataclasses
import json

import os
import logging
import tempfile

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from config import DATA_DIR
from core.models import POSITION_CLASS_MAP

JSON_ROOT = os.path.join(DATA_DIR, "json")

logger = logging.getLogger(__name__)
# ---- Helpers ----
def normalize_position(position: str) -> str:
    '''

    :param position:
    :return:
    '''
    pos = (position or "").strip().upper()
    if pos not in POSITION_CLASS_MAP:
        raise ValueError(f"Invalid position: {position}")

    return pos

def position_filename(position: str) -> str:
    '''

    :param position:
    :return:
    '''
    return f"draft_{normalize_position(position)}.json"

def year_directory(year: int) -> str:
    '''

    :param year:
    :return:
    '''
    return os.path.join(JSON_ROOT, str(year))

def position_path(year: int, pos: str) -> str:
    '''

    :param year:
    :param pos:
    :return:
    '''
    return os.path.join(year_directory(year), position_filename(pos))


def write_json(filepath: str, data: Dict[str, Any]) -> None:
    '''

    :param filepath:
    :param data:
    :return:
    '''

    dir = os.path.dirname(filepath)
    os.makedirs(dir, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=dir) as temp_file:
        json.dump(data, temp_file, ensure_ascii=False, indent=2)
        temp = temp_file.name
    os.replace(tmp, filepath)

def read_json(filepath: str) -> Optional[Dict[str, Any]]:
    '''

    :param filepath:
    :return:
    '''
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Corrupt JSON File at {filepath}: {e}")
        return None

def draftee_list_to_dicts(players: Iterable[Any]) -> List[Dict[str, Any]]:
    '''

    :param players:
    :return:
    '''
    res = List[Dict[str, Any]] = []
    seen: set = set()
    for player in players or []:
        player_dict = dataclasses.asdict(player) if dataclasses.is_dataclass(player) else None
        if player_dict is None:
            logger.warning(f"Player not a dataclass {player}")
            continue

        key = (player_dict.get("name"), player_dict.get("college"), player_dict.get("pick"))
        if key in seen:
            continue

        seen.add(key)
        res.append(player_dict)

    return res


class DrafteeStorage