'''
Calls CollegeFootballData.com API
'''

from functools import lru_cache
import logging
from typing import Dict, Any, List

import pandas as pd

from .. import config
from .http import HttpClient
from .http import get_client

logger = logging.getLogger(__name__)

_API_ROOT = config.CFBD_API_ROOT

# ---- Helper Functions ----
def _client(client: http.HttpClient = None) -> http.HttpClient:
    return client or get_default_client()

def _get_json(endpoint: str,
              *, client: http.HttpClient = None, **params: Any)

    request_url = f"{_API_ROOT}{endpoint}"
    headers = config.cfbd_headers()

    response = _client(client).get(request_url, headers=headers, params=params)
    try:
        return response.json()
    except ValueError as e:
        logger.error(f"[ERROR] Failed to parse JSON from {request_url}: {e}")
        raise



# ---- Public Functions ----
@lru_cache(maxsize=1)
def get_stat_type_map(
        *, client: HttpClient = None) -> Dict[str, int]:
    '''
    Returns mapping {stat_name: stat_id}
    :param client:
    :return:
    '''

    data = _get_json("plays/stats/types", client=client)
    df = pd.json_normalize(data)
    return df.set_index("name")["id"].astype(int).to_dict()

@lru_cache(maxsize=1)
def get_play_type_map(
        *, client: HttpClient = None) -> Dict[str, int]:
    '''
    Returns mapping {play_type_text: play_type_id}
    :param client:
    :return:
    '''
    data = _get_json("plays/types", client=client)
    df = pd.json_normalize(data)
    return df.set_index("text")["id"].astype(int).to_dict()

def search_athlete(name: str,
                   *, team: str = None, position: str = None,
                   client: HttpClient = None) -> pd.DataFrame:
    '''
    Search /player/search and return a pd.DataFrame of matches
    :param name:
    :param team:
    :param position:
    :param client:
    :return:
    '''

    params: Dict[str, Any] = {"seachTerm": name}
    if team:
        params["team"] = team
    if position:
        params["position"] = position

    data = _get_json("player/search", client=client, **params)
    return pd.json_normalize(data)


