'''
Defines classes for players and positional stats.
'''

from dataclasses import dataclass
from dataclasses import asdict
from dataclasses import field
from test.test_typing import Position

from typing import Dict
from typing import Any
from typing import Type


# ---- Define base Player class ----
@dataclass()
class Player:
    '''Common attritbutes amongst all athletes'''

    name      : str
    position  : str
    age       : int = None
    height    : int = None
    height    : int = None
    weight    : int = None
    college   : str = None
    stats_link: str = None

    def __dict__(self):
        '''return a dictionary mapping (attribute -> value) of object'''
        return asdict(self)


# ---- Define Statiscal Standards (Rushing, Receiver, Defense) ----
@dataclass()
class RushingStandard:
    rush_att: int = None
    rush_yds: int = None
    yush_td : int = None

@dataclass()
class ReceivingStandard:
    rec     : int = None
    rec_yds : int = None
    rec_tds : int = None

@dataclass()
class DefensiveStandard:
    tackles_solo  : int = None
    tackle_assists: int = None
    tackles_loss  : int = None
    sacks         : int = None
    def_int       : int = None
    pass_defended : int = None
    fumbles_rec   : int = None
    fumbles_forced: int = None

# ---- Define Positional Groups ----
@dataclass()
class Quarterback(Player, RushingStandard):
    games       : int = None
    pass_cmp_pct: int = None
    pass_yds    : int = None
    pass_td     : int = None
    pass_int    : int = None
    pass_rating : int = None

@dataclass()
class Runningback(Player, RuhsingStandard, ReceivingStandard):
    games : int = None

@dataclass()
class WideReceiver(Player, RushingStandard, ReceivingStandard):
    games : int = None

@dataclass()
class OffensiveLinemen(Player):
    games: int = None

@dataclass()
class DefensiveLinemen(Player, DefensiveStandard):
    games: int = None

@dataclass()
class Cornerback(Player, DefensiveStandard):
    games      : int = None
    def_int_yds: int = None
    fumble_rec_yds: int = None

@dataclass()
class Linebacker(Player, DefensiveStandard):
    games      : int = None
    def_int_yds: int = None


# ---- map position abbreviation to proper class ----
POSITION_CLASS_MAP: Dict[str, Type[Player]] = {
    "QB": Quarterback,
    "RB": Runningback,
    "WR": WideReceiver,
    "OL": OffensiveLinemen,
    "DT": DefensiveLinemen,
    "CB": Cornerback,
    "OLB": Linebacker,
}

def get_position_class(position: str, **kwargs: Any) -> Player:
    '''Returns proper subclass from positional abbreviation'''

    #uppercase for sanity
    position = position.upper()

    position_class = POSITION_CLASS_MAP.get(position, None)
    if position_class is None:
        raise ValueError(f"[ERROR] Invalid Position: {position} <get_position_class>")
    return position_class(position=position, **kwargs)
