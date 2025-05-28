'''
HTML parsers for Pro-Football-Reference pages.
'''

import re
from typing import List, Dict, Any

from bs4 import BeautifulSoup
from bs4 import Tag

from prospect_clustering import config
from pos_models import Player, get_position_class

# ---- Define positional attributes
POSITION_SCHEMA = {
    "QB": {
        "standards": {
            "passing_standard": [
                "games", "pass_att", "pass_cmp_yds", "pass_yds", "pass_int", "pass_rating"
            ],
            "rushing_standard": ["rush_att", "rush_yds", "rush_td"],
        },
        "type_int": {
            "games", "pass_yds", "pass_td", "pass_int", "rush_att", "rush_yds", "rush_td"
        },
    },
    "RB": {
        "standards": {
            "rushing_standard": [
                "games", "rush_att", "rush_yds", "rush_td", "rec", "rec_yds", "rec_td"]
        },
        "type_int": {
            "games", "rush_att", "rush_yds", "rush_td", "rec", "rec_yds", "rec_td"
        }
    },
    "WR": {
        "standards": {
            "receiving_standard": [
                "games", "rec", "rec_yds", "rec_td", "rush_att", "rush_yds", "rush_td",
            ]
        },
        "type_int": {
            "games", "rec", "rec_yds", "rec_td", "rush_att", "rush_yds", "rush_td"
        },
    },
    "OL": {
        "standards": {
            "defense_standard": ["games"]
        },
        "type_int": {"games"},
    },
    "DT": {
        "sections": {
            "defense_standard": [
                "games", "tackles_solo", "tackles_assists", "tackles_loss", "sacks", "def_int", "pass_defended", "fumbles_rec", "fumble_rec_yds", "fumbles_forced",
            ]
        },
        "type_int": {
            "games", "rec", "rec_yds", "rec_td", "rush_att", "rush_yds", "rush_td",
        },
    },
    "CB": {
        "standards": {
            "defense_standard": [
                "games", "tackles_solo", "tackles_assists", "tackles_loss", "def_int", "def_int_yds", "pass_defended", "fumbles_rec", "fumbles_forced",
            ]
        },
        "type_int": {
            "games", "tackles_solo", "tackles_assists", "tackles_loss", "def_int", "def_int_yds", "pass_defended", "fumbles_rec", "fumble_rec_yds", "fumbles_forced",
        },
    },
    "OLB": {
        "standards": {
            "defense_standard": [
                "games", "tackles_solo", "tackles_assists", "tackles_loss", "def_int", "def_int_yds", "pass_defended", "fumbles_rec", "fumble_rec_yds", "fumbles_forced",
            ]
        },
        "type_int": {
            "games", "tackles_solo", "tackles_assists", "tackles_loss", "def_int", "def_int_yds", "pass_defended", "fumbles_rec", "fumble_rec_yds", "fumbles_forced"
        },
    },
}


# ---- Helper Functions ----

def _clean_cell(cell: Tag) -> str:
    return cell.text.strip() if cell else None

def _to_int(text: str) -> int:
    return int(text) if text and text.isdigit() else None

def _to_float(text: str) -> float:
    return float(text) if text and text.isdecimal() else None

def _height_to_inches(height: float) -> int:
    if not raw or "-" not in raw:
        return None
    feet, inches = raw.split("-")
    try:
        return int(feet) * 12 + int(inches)
    except ValueError:
        return None


# ---- PFR Parsing ----
def parse_prospect_page(html: str) -> Dict[str, List[Player]]:
    soup = BeautifulSoup(html, "html.parser")
    all_players = {}

    for pos in POSITION_SCHEMA.keys():
        table = soup.find("table", {"id": f"prospects_{POS}"})
        if table is None:
            continue

        rows = table.tbody.find_all("tr", recursive=False)
        players: List[Player] = []

        for row in rows:
            name_cell = row.find("th", {"data-stat": "player"})
            if not name_cell:
                continue
            name = _clean_cell(name_cell)

            age    = _to_int(_clean_cell(row.find("td", {"data-stat": "age"})))
            height = _clean_cell(row.find("td", {"data-stat": "height"}))
            height = _height_to_inches(height)
            weight = _to_int(_clean_cell(row.find("td", {"data-stat": "weight"})))
            college = _clean_cell(row.find("td", {"data-stat": "college_name"}))

            try:
                href = row.find("td", {"data-stat": "cfb"}).a['href']
            except Exception:
                href = None

            player = get_position_class(
                position=pos,
                name=name,
                age=age,
                height=height,
                weight=weight,
                college=college,
                stats_link=href,
            )
            players.append(player)
        all_players[pos] = players
    return all_players


def parse_player_page(html: str, player: Player) -> Player:

    if player.position not in POSITION_SCHEMA:
        raise ValueError(f"[ERROR] Invalid position {player.position}")

    soup = BeautifulSoup(html, "html.parser")

    position_schema = POSITION_SCHEMA[player.position]
    for table_id, fields in position_schema['standards'].items():
        table = soup.find("table", {"id": table_id})
        if not table or not table.tfoot:
            continue

        career_row = table.tfoot.find("tr", {"id": f"{table_id}.Career"})
        if career_row is None:
            continue

        for field in fields:
            cell = career_row.find("td", {"data-stat": field})
            raw_text = _clean_cell(cell)

            if field in schema['type_int']:
                value = _to_int(raw_text)
            else:
                value = _to_float(raw_text)
            setattr(player, field, value)
        return player