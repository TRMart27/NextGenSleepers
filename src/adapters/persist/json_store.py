""" """
import dataclasses
import json

import os
import logging
import tempfile

from typing import Any, Dict, Iterable, List, Optional, Tuple

from src.config import DATA_DIR
from src.core.models import POSITION_CLASS_MAP

JSON_ROOT = os.path.join(DATA_DIR, "json")

logger = logging.getLogger(__name__)


# ---- Helpers ----
def normalize_position(position: str) -> str:
    """

    :param position:
    :return:
    """
    pos = (position or "").strip().upper()
    if pos not in POSITION_CLASS_MAP:
        raise ValueError(f"Invalid position: {position}")

    return pos


def position_filename(position: str) -> str:
    """

    :param position:
    :return:
    """
    return f"draft_{normalize_position(position)}.json"


def year_directory(year: int) -> str:
    """

    :param year:
    :return:
    """
    return os.path.join(JSON_ROOT, str(year))


def position_path(year: int, pos: str) -> str:
    """

    :param year:
    :param pos:
    :return:
    """
    return os.path.join(year_directory(year), position_filename(pos))


def generate_key(row: Dict[str, Any]) -> Tuple[Any, Any, Any]:
    return (row.get("name"), row.get("college"), row.get("pick"))


def prepare_payload(year: int, pos: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "year": int(year),
        "position": normalize_position(pos),
        "player_count": len(data),
        "data": data,
    }


# ---- File Handling ----
def write_json(filepath: str, data: Any) -> None:
    """

    :param filepath:
    :param data:
    :return:
    """

    json_dir = os.path.dirname(filepath)
    os.makedirs(json_dir, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "a", delete=False, encoding="utf-8", dir=json_dir
    ) as temp_file:
        json.dump(data, temp_file,ensure_ascii=False, indent=2)
        temp_filepath = temp_file.name
    os.replace(temp_filepath, filepath)


def read_json(filepath: str) -> Optional[Dict[str, Any]]:
    """

    :param filepath:
    :return:
    """
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Corrupt JSON File at {filepath}: {e}")
        return None


def draftee_list_to_dicts(players: Iterable[Any]) -> List[Dict[str, Any]]:
    """

    :param players:
    :return:
    """
    res = List[Dict[str, Any]] = []
    seen: set = set()
    for player in players or []:
        player_dict = (
            dataclasses.asdict(player) if dataclasses.is_dataclass(player) else None
        )
        if player_dict is None:
            logger.warning(f"Player not a dataclass {player}")
            continue

        key = (
            player_dict.get("name"),
            player_dict.get("college"),
            player_dict.get("pick"),
        )
        if key in seen:
            continue

        seen.add(key)
        res.append(player_dict)

    return res


class DrafteeStorage:
    def __init__(self, root: Optional[str] = None) -> None:
        self._root = root or JSON_ROOT
        # ensure dir exists
        os.makedirs(self._root, exist_ok=True)

        def load(self, year: int, position: str) -> List[Dict[str, Any]]:
            """

            :param self:
            :param year:
            :param position:
            :return:
            """
            filepath = position_path(year, position)
            json_payload = read_json(filepath)
            if not json_payload:
                return []

            if json_payload.get("year") != year or normalize_position(
                json_payload.get("position", "")
            ) != normalize_position(position):
                logger.warning(f"Malformed header in file: {filepath}")

            data = json_payload.get("data") or []
            if not isinstance(data, list):
                logger.error(f"Malformed data for file: {filepath}, got {type(data)}")
                return []

            return data

        def list_years(self) -> List[int]:
            """

            :param self:
            :return:
            """
            years: List[int] = []
            if not os.path.isdir(self._root):
                return years
            for dir_name in os.listdir(self._root):
                if dir_name.isdigit():
                    years.append(int(dir_name))
            # sort for readability
            years.sort()
            return years

        def list_positions_for_year(self, year: int) -> List[str]:
            """

            :param self:
            :param year:
            :return:
            """
            year_dir = year_directory(year=year)
            if not os.path.isdir(year_dir):
                return []

            res: List[str] = []
            for filename in os.listdir(year_dir):
                if filename.startswith("draft_") and filename.endswith(".json"):
                    res.append(filename[len("draft_") : -len(".json")])
            return res
