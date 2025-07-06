'''
Sports-Reference / Pro-Football-Reference specific
FETCHERS ONLY - DOES NOT PARSE, only acts as an inbetween
user and http.py
'''

import datetime as _dt

import config
from scrape.http import HttpClient
import scrape.http as http


#get the year ranges
_MIN_YEAR = 1936
_MAX_YEAR = _dt.date.today().year

def _validate_year(year: int) -> None:
    if not (_MIN_YEAR <= year <= _MAX_YEAR):
        raise ValueError(f'[ERROR] Years must be between '
                         f'{_MIN_YEAR} and {_MAX_YEAR}')


# ---- Build URLS using ROOTS ----
def prospects_url(year: int) -> str:
    '''
    :param year: Year to look for draft prospects
    :return: string URL to PFR
    '''
    _validate_year(year)
    return f"{config.PFR_PROSPECTS_ROOT}{year}_prospects.htm"


def draft_url(year: int) -> str:
    '''
    :param year: Year to look at DRAFTED prospects from previous drafts
    :return: string URL to PFR
    '''
    _validate_year(year)
    return f"{config.PFR_DRAFT_ROOT}{year}/draft.htm"


# ---- HTTPClient wrappers ----
def _http_client(client: HttpClient) -> None:
    return client or http.get_client()


def fetch_prospects_page(year: int,
                         *, client: HttpClient = None) -> str:
    """
    Download the HTML for <year>

    :param year  : Year to look for draft prospects
    :param client: OPTIONAL HTTPClient besides default
    :return      : HTML page as string
    """

    request_url = prospects_url(year)
    return _http_client(client).send_request(request_url).text

def fetch_draft_page(year: int,
                     *, client: HttpClient = None) -> str:
    """
    Download the HTML for <year>

    :param year  : Year to look for draft prospects
    :param client: OPTIONAL HTTPClient besides default
    :return      : HTML page as string
    """
    request_url = draft_url(year)
    return _http_client(client).send_request(request_url).text

def fetch_player_page(href: str,
                      *, client: HttpClient = None) -> str:
    '''
    Download single players college-stats page

    :param href  : URL to players college-stats
    :param client: OPTIONAL HttpClient besides default
    :return      : HTML page as string
    '''
    if not href:
        raise ValueError("[ERROR] No URL provided! <fetch_player_page>")

    if not href.startswith('http'):
        href = f"https://www.sports-reference.com{href}"
    return _http_client(client).send_request(href).text
