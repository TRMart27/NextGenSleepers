"""
Defines classes for players and positional stats.
"""

from dataclasses import dataclass

from typing import Dict, Type, TypeVar, Generic, Optional

T = TypeVar("T")


@dataclass()
class NFLDraftee(Generic[T]):
    player: T
    pick: int = None
    career_av: int = None


# ---- Define base Player class ----
@dataclass()
class Player:
    """Common attritbutes amongst all athletes"""

    name: Optional[str] = None
    position: Optional[str] = None
    age: Optional[int] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    college: Optional[str] = None
    stats_link: Optional[str] = None


# ---- Define Positional Groups ----
@dataclass()
class Quarterback(Player):
    games: Optional[int] = None
    games_started: Optional[int] = None
    pass_cmp_pct: Optional[float] = None
    pass_yds: Optional[int] = None
    pass_td: Optional[int] = None
    pass_att: Optional[int] = None
    pass_int: Optional[int] = None
    pass_rating: Optional[float] = None
    rush_att: Optional[int] = None
    rush_yds: Optional[int] = None
    rush_td: Optional[int] = None


@dataclass()
class Runningback(Player):
    games: Optional[int] = None
    rush_att: Optional[int] = None
    rush_yds: Optional[int] = None
    rush_td: Optional[int] = None
    rec: Optional[int] = None
    rec_yds: Optional[int] = None
    rec_td: Optional[int] = None


@dataclass()
class WideReceiver(Player):
    games: Optional[int] = None
    rec: Optional[int] = None
    rec_yds: Optional[int] = None
    rec_td: Optional[int] = None
    rush_att: Optional[int] = None
    rush_yds: Optional[int] = None
    rush_td: Optional[int] = None


@dataclass()
class OffensiveLinemen(Player):
    games: Optional[int] = None


@dataclass()
class DefensiveLinemen(Player):
    games: Optional[int] = None
    tackles_solo: Optional[int] = None
    tackles_assists: Optional[int] = None
    tackles_loss: Optional[int] = None
    sacks: Optional[float] = None
    def_int: Optional[int] = None
    pass_defended: Optional[int] = None
    fumbles_rec: Optional[int] = None
    fumbles_forced: Optional[int] = None


@dataclass()
class Cornerback(Player):
    games: Optional[int] = None
    tackles_solo: Optional[int] = None
    tackles_assists: Optional[int] = None
    tackles_loss: Optional[int] = None
    def_int: Optional[int] = None
    pass_defended: Optional[int] = None
    fumbles_rec: Optional[int] = None
    fumbles_forced: Optional[int] = None
    def_int_yds: Optional[int] = None
    fumble_rec_yds: Optional[int] = None


@dataclass()
class Linebacker(Player):
    games: Optional[int] = None
    tackles_solo: Optional[int] = None
    tackles_assists: Optional[int] = None
    tackles_loss: Optional[int] = None
    sacks: Optional[float] = None
    def_int: Optional[int] = None
    pass_defended: Optional[int] = None
    fumbles_rec: Optional[int] = None
    fumbles_forced: Optional[int] = None
    def_int_yds: Optional[int] = None


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


def make_player(position: str, **kwargs) -> Player:
    """

    :param position:
    :param kwargs:
    :return:
    """
    position = position.upper()
    position_class = POSITION_CLASS_MAP.get(position)
    if position_class is None:
        raise ValueError(f"[ERROR] Invalid Position: {position} <make_player>")
    return position_class(position=position, **kwargs)


def make_draftee(
    position: str, *, pick: int, career_av: Optional[int] = None, **kwargs
) -> NFLDraftee[Player]:
    """

    :param position:
    :param pick:
    :param career_av:
    :param kwargs:
    :return:
    """

    player = make_player(position, **kwargs)
    return NFLDraftee(player=player, pick=pick, career_av=career_av)
