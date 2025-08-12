"""
Central settings, magic constants and environment variable helpers
for the project.
"""

import os
from pathlib import Path
from typing import Final, List, Dict

# ---- Define Paths ---- #

BASE_DIR: Final[Path] = Path(__file__).parent.resolve()
DATA_DIR: Final[Path] = BASE_DIR / "data"
CACHE_DIR: Final[Path] = BASE_DIR / "cache"


# ---- Make Directories ---- #
DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)


# ---- Networking Config ---- #
USER_AGENT: Final[str] = (
    "prospect_clustering-bot/1.0 (+https://github.com/TRMart27/NextGenSleepers)"
)

REQUEST_COOLDOWN: Final[int] = int(os.getenv("PFR_REQUEST_COOLDOWN", "10"))
REQUEST_JAIL: Final[int] = int(os.getenv("PFR_REQUEST_JAIL", "3600"))
REQUEST_MAX: Final[int] = int(os.getenv("PFR_REQUEST_MAX", "1"))
MAX_RETIRES: Final[int] = int(os.getenv("PFR_MAX_RETIRES", "3"))
BACKOFF_FACTOR: Final[float] = float(os.getenv("PFR_BACKOFF_FACTOR", 3.0))

# ---- Website Roots ---- #

PFR_PROSPECTS_ROOT: Final[str] = "https://www.pro-football-reference.com/draft/"
PFR_DRAFT_ROOT: Final[str] = "https://www.pro-football-reference.com/years/"
CFBD_API_ROOT: Final[str] = "https://api.collegefootballdata.com/"

# ---- Secrets ---- #

CFBD_API_KEY: Final[str | None] = os.getenv(
    "CFBD_API_KEY", "cij65DpP8rbi7c252kjeJCgscF6hYtuwDXH2EaIO7ULRJO7+4uaFTzzkx7hvuyVh"
).strip()
if CFBD_API_KEY is None:
    print("[ERROR] CFBD API Key not loaded!")


def cfbd_headers() -> Dict[str, str]:
    """
    :return: Authorization header for CollegeFootballData API calls

    :raises RuntimeError if CFBD_API_KEY is missing
    """

    if CFBD_API_KEY is None:
        raise RuntimeError("[ERROR] CFBD_API_KEY not set")

    return {"Authorization": f"Bearer {CFBD_API_KEY}"}

    # ---- Selenium Flags ---- #


SELENIUM_FLAGS: Final[List[str]] = [
    "--headless",
    "--disable-gpu",
    "--no-sandbox",
    "--disable-dev-shm-usage",
]


# ---- Position Map ---- #
NFL_POSITION_MAP: Final[Dict[str, str]] = {
    "QB": "QB",
    "RB": "RB",
    "WR": "WR",
    "TE": "WR",
    "T": "OL",
    "G": "OL",
    "C": "OL",
    "OT": "OL",
    "OG": "OL",
    "OL": "OL",
    "DE": "DT",
    "DT": "DT",
    "DL": "DT",
    "CB": "CB",
    "DB": "CB",
    "S": "CB",
    "SAF": "CB",
    "FS": "CB",
    "LB": "OLB",
    "OLB": "OLB",
}