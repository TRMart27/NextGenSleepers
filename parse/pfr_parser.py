'''
HTML parsers for Pro-Football-Reference pages.
'''

import re
from typing import List, Dict, Any
from collections import defaultdict

import pos_models
from bs4 import BeautifulSoup
from bs4 import Tag
from bs4 import Comment

import config
from pos_models import Player
from pos_models import get_position_class
from pos_models import NFLDraftee

# ---- Define positional attributes
POSITION_SCHEMA = {
    "QB": {
        "standards": {
            "passing_standard": [
                "games", "games_started", "pass_att", "pass_td", "pass_cmp_pct", "pass_yds", "pass_int", "pass_rating"
            ],
            "rushing_standard": ["rush_att", "rush_yds", "rush_td"],
        },
        "type_int": {
            "games", "pass_yds", "pass_td", "pass_att", "pass_int", "rush_att", "rush_yds", "rush_td"
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
        "standards": {
            "defense_standard": [
                "games", "tackles_solo", "tackles_assists", "tackles_loss", "sacks", "def_int", "pass_defended", "fumbles_rec", "fumbles_forced",
            ]
        },
        "type_int": {
            "games", "tackles_solo", "tackles_assists", "tackles_loss", "def_int", "pass_defended", "fumbles_rec", "fumble_rec_yds", "fumbles_forced",
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
                "games", "tackles_solo", "tackles_assists", "tackles_loss", "sacks", "def_int", "def_int_yds", "pass_defended", "fumbles_rec", "fumble_rec_yds", "fumbles_forced",
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
    if text is None:
        return None
    try:
        return int(text.strip())
    except ValueError:
        return None

def _to_float(text: str) -> float:
    if text is None:
        return None
    try:
        return float(text.strip())
    except ValueError:
        return None

def _height_to_inches(height: float) -> int:
    if not height or "-" not in height:
        return None
    feet, inches = height.split("-")
    try:
        return int(feet) * 12 + int(inches)
    except ValueError:
        return None

def _uncomment_tables(html: str) -> str:
    '''
    Helper function to uncomment the position
    tables from the raw html

    :param html:
    :return:
    '''
    soup = BeautifulSoup(html, "html.parser")

    for node in soup.find_all(text=True):
        #if node is a comment with <table tag
        if isinstance(node, Comment) and "<table" in node:
            #replace with itself
            table_fragment = BeautifulSoup(node, "html.parser")
            node.replace_with(table_fragment)

    return str(soup)

# ---- PFR Parsing ----
def parse_prospect_page(html: str) -> Dict[str, List[Player]]:
    #ensure all tables are present
    html = _uncomment_tables(html)

    #soupify
    soup = BeautifulSoup(html, "html.parser")
    all_players = {}

    for pos in POSITION_SCHEMA.keys():
        table = soup.find("table", {"id": f"prospects_{pos}"})
        if table is None:
            print(f"[ERROR] Failed to find table for {pos}")
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

def parse_draft_page(html: str) -> Dict[str, List[Player]]:
    '''

    :param html:
    :return:
    '''
    #soupify
    soup = BeautifulSoup(html, "html.parser")
    all_players = defaultdict(list)

    table = soup.find("table", {"id": "drafts"})
    if not table or table.tfoot:
        print("[ERROR] No table found")
        return None

    for row in table.tbody.find_all("tr"):
        position = _clean_cell(row.find("td", {"data-stat": "pos"}))
        name     = _clean_cell(row.find("td", {"data-stat": "player"}))
        age      = _to_int(_clean_cell(row.find("td", {"data-stat": "age"})))
        college  = _clean_cell(row.find("td", {"data-stat": "college_id"}))

        try:
            href = row.find("td", {"data-stat": "college_link"}).a['href']
        except:
            href = None

        if position not in config.NFL_POSITION_MAP.keys():
            continue

        #draftee
        pick     = _to_int(_clean_cell(row.find("td", {"data-stat": "draft_pick"})))
        career_av = _to_int(_clean_cell(row.find("td", {"data-stat": "career_av"})))
        mapped_position = config.NFL_POSITION_MAP[position]

        player = get_position_class(
            position=mapped_position,
            name=name,
            age=age,
            college=college,
            stats_link=href,
            \
            pick=pick,
            career_av=career_av
        )

        if not isinstance(player, NFLDraftee):
            print(f'[WARNING] Something went wrong bro - {name}')

        all_players[mapped_position].append(player)
    return all_players




def parse_player_page(html: str, player: Player) -> Player:

    if player.position not in POSITION_SCHEMA:
        raise ValueError(f"[ERROR] Invalid position {player.position}")

    soup = BeautifulSoup(html, "html.parser")
    all_players = {}

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
            if field in position_schema['type_int']:
                value = _to_int(raw_text)
            else:
                value = _to_float(raw_text)
            setattr(player, field, value)
    return player


def parse_height_weight(html: str, athlete):
    '''

    :param html:
    :param player:

    :return:
    '''
    soup = BeautifulSoup(html, "html.parser")
    re_height_weight = re.compile(r"\b\d{1,2}-\d{1,2}\b")

    for p in soup.find_all("p"):
        if "lb" not in p.get_text():
            continue

        spans = p.find_all("span")
        if len(spans) < 2:
            continue

        height_text = spans[0].get_text(strip=True)
        weight_text = spans[1].get_text(strip=True)

        if not re_height_weight.fullmatch(height_text) or not weight_text.endswith("lb"):
            continue

        feet, inch = map(int, height_text.split("-"))

        height = feet * 12 + inch
        weight = int(re.sub(r"\D", "", weight_text))

        athlete.player.height = height
        athlete.player.weight = weight

        return
