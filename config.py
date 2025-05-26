'''
Central settings, magic constants and environment variable helpers
for the project. Keeps all hard coded strings in one place to keep
everything else nice and clean.
'''
from __future__ import Annotations

import os
from pathlib import Path
from typing import Final, List, Dict

                        # ---- Define Paths ---- #

BASE_DIR : Final[Path] = Path(__file__).parent.resolve().parent
DATA_DIR : Final[Path] = BASE_DIR / "data"
CACHE_DIR: Final[Path] = BASE_DIR / "cache"


                        # ---- Make Directories ---- #
DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)


                        # ---- Networking Config ---- #
USER_AGENT: Final[str] = (
    "prospect_clustering-bot/1.0"
    "(+https://github.com/TRMart27/NextGenSleeper)"
)

REQUEST_COOLDOWN: Final[int] = int(os.getenv("PFR_REQUEST_COOLDOWN"), "60")
REQUEST_JAIL    : Final[int] = int(os.getenv("PFR_REQUEST_JAIL"), "3600")
MAX_RETIRES     : Final[int] = int(os.getenv("PFR_MAX_RETIRES"), "3")
BACKOFF_FACTOR  : Final[float] = float(os.getenv("PFR_BACKOFF_FACTOR", "3.0"))

                        # ---- Website Roots ---- #

PFR_PROSPECTS_ROOT: Final[str] = "https://www.pro-football-reference.com/drafts/"
PFR_DRAFT_ROOT:     Final[str] = "https://www.pro-football-reference.com/years/"
CFBD_API_ROOT:      Final[str] = "https://api.collegefootballdata.com/"

                        # ---- Secrets ---- #

CFBD_API_KEY: Final[str | None] = os.getenv("CFBD_API_KEY")



def cfbd_headers() -> Dict[str, str]:
    '''
    :return: Authorization header for CollegeFootballData API calls

    :raises RuntimeError if CFBD_API_KEY is missing
    '''

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
NFL_POSITION_MAP: Final[Dict[str, List[str]]] = {
    "QB": "QB",
    "RB": "RB",
    "WR": "WR",
    "TE": "WR",
    "T": "OL",
    "G": "OL",
    "T": "OL",
    "DE": "DT",
    "DT": "DT",
    "CB": "CB",
    "S": "CB",
    "LB": "OLB",
}


NFL_COMPARISONS = {
    "QB": [
        "Patrick Mahomes", "Josh Allen", "Jalen Hurts", "Joe Burrow",
        "Lamar Jackson", "Justin Herbert", "Kirk Cousins", "Dak Prescott",
        "Daniel Jones", "Jared Goff", "Geno Smith", "Tua Tagovailoa",
        "Sam Darnold", "Zach Wilson", "Davis Mills", "Mac Jones", "Andy Dalton"],
    "RB": [
        "Christian McCaffrey", "Derrick Henry", "Saquon Barkley",
        "Jonathan Taylor", "Bijan Robinson", "Josh Jacobs", "Aaron Jones",
        "Joe Mixon", "Travis Etienne", "Najee Harris", "Tony Pollard",
        "Rhamondre Stevenson", "Michael Carter", "Damien Harris",
        "Nyheim Hines", "Phillip Lindsay", "Antonio Gibson"],
    "WR": [
        "Justin Jefferson", "Tyreek Hill", "A.J. Brown", "Ja'Marr Chase",
        "Davante Adams", "Stefon Diggs", "Keenan Allen", "Mike Evans",
        "CeeDee Lamb", "Van Jefferson", "Randall Cobb"],

    "TE": [
        "Travis Kelce", "George Kittle", "T.J. Hockenson", "Dallas Goedert",
        "O.J. Howard", "Hunter Henry", "Anthony Firkser"],

    "T": [
        "Trent Williams", "Penei Sewell", "Ryan Ramczyk", "Lane Johnson",
        "Terron Armstead", "Jonah Williams", "Cedric Ogbuehi", "Chukwuma Okorafor"],
    "G": [
        "Quenton Nelson", "Zack Martin", "Brandon Scherff", "Joel Bitonio",
        "Wyatt Teller", "Justin Pugh", "Matt Feiler", "Jermaine Eluemunor",
        "Michael Onwenu", "Jason Kelce"],

    "DT": [
        "Aaron Donald", "Chris Jones", "Quinnen Williams", "Dalvin Tomlinson",
        "Jeffery Simmons", "Dre'Mont Jones", "Da'Ron Payne", "Dexter Lawrence",
        "Al Woods", "Mike Pennel", "Jarran Reed", "Jordan Phillips"],

    "DE": [
        "Nick Bosa", "Myles Garrett", "Danielle Hunter", "Cameron Jordan",
        "Calais Campbell", "Solomon Thomas"],

    "CB": [
        "Jalen Ramsey", "Sauce Gardner", "Patrick Surtain II",
        "Marshon Lattimore", "Tre'Davious White", "Darius Slay",
        "Carlton Davis", "Rasul Douglas", "Jaylon Johnson", "Bryce Hall",
        "Bless Austin", "Elijah Molden", "Mike Hughes", "Chandon Sullivan", "Marco Wilson"],

    "S": [
        "Jessie Bates III", "Justin Simmons"],

    "LB": [
        "T.J. Watt", "Micah Parsons", "Lavonte David", "Khalil Mack",
        "Matthew Judon", "Haason Reddick", "Fred Warner", "Demario Davis", "Roquan Smith", "Bobby Wagner",
        "Foyesade Oluokun", "Myles Jack", "Devin White", "Cole Holcomb",
        "Christian Kirksey", "Anthony Walker Jr.", "Elandon Roberts",
        "Joe Thomas"]
}
