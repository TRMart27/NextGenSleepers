'''
JSON Helpers
'''
import pos_models as Models
import os
import json
import pandas as pd

from typing import Dict
from typing import List
from dataclasses import asdict

def send_to_json(draftees: List[Models.NFLDraftee], filepath: str) -> None:
    """
    Serialize a list of NFLDraftee dataclasses (which contain nested dataclasses)
    to JSON at the given filepath.
    """
    # Convert each NFLDraftee (and its nested player) to a dictionary
    data = [asdict(nfl) for nfl in draftees]
    try:
        with open(filepath, "w", encoding="utf-8") as file_ref:
            json.dump(data, file_ref, indent=2)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return


def load_json(filepath: str) -> pd.DataFrame:
    ''' Load single JSON file'''
    if not filepath.endswith(".json"):
        print("[ERROR] Filepath is not a .json!")
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as file_ref:
            data = json.load(file_ref)
            return pd.json_normalize(data)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return None


def parse_position_json(data) -> List[Models.NFLDraftee]:
    '''

    :param data:
    :return:
    '''
    player_list = []

    for player_dict in data:
        position = ""
        profile  = None
        pick     = None
        career_av = None

        for key, value in player_dict.items():
            if key == ('player'):
                position = value.pop('position')
                profile  = value
            elif key == ('pick'):
                pick = value
            else:
                career_av = value

        draftee = Models.get_position_class(position,
                                        **profile,
                                        pick=pick,
                                        career_av=career_av)
        player_list.append(draftee)
    return player_list

