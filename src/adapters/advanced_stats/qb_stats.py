import src.adapters.scrape.cfbd_scraper as cfbd_scraper


def to_lower(s: str) -> str:
    return (s or "").lower()


def is_qb_involved(play, qb_name: str) -> bool:
    return qb_name.lower() in to_lower(getattr(play, "play_text", ""))

def is_pass(play) -> bool:
    return to_lower(getattr(play, "play_text", "")).startswith("pass")

def is_sack(play, qb_name: str) -> bool:
    play_type = to_lower(getattr(play, "play_type", ""))
    play_text = to_lower(getattr(play, "play_text", ""))
    return ("sack" in play_text and is_qb_involved(play, qb_name)) or (play_type == "sack")

def is_scramble(play, qb):
    return play.play_type == "Rush" and qb.lower() in play.play_text.lower() and "scramble" in play.play_text.lower()

def is_long_down(play) -> bool:
    return getattr(play, "down", 0) in (2, 3) and (getattr(play, "distance", 0) or 0) >= 7

def is_conversion_text(text_lower: str) -> bool:
    return ("for a 1st down" in text_lower) or ("for a td" in text_lower) or ("touchdown" in text_lower)

def compute_sack_rate(plays, qb_name: str):
    attempts = 0
    sacks = 0
    scrambles = 0
    for play in plays:
        if is_qb_involved(play, qb_name):
            if is_pass(play):
                attempts += 1
            if is_sack(play, qb_name):
                sacks += 1
            if is_scramble(play, qb_name):
                scrambles += 1

    dropbacks = attempts + sacks + scrambles
    return {
        "qb": qb_name,
        "attempts": attempts,
        "sacks": sacks,
        "dropbacks": dropbacks,
        "sack_rate": (sacks / dropbacks) if dropbacks else 0.0,
    }


def compute_long_conversion_rate(plays, qb_name: str):
    attempts = 0
    conversions = 0
    for play in plays:
        if is_long_down(play) and is_qb_involved(play, qb_name):
            attempts += 1
            if is_conversion_text(to_lower(getattr(play, "play_text", ""))):
                conversions += 1
    return {
        "qb": qb_name,
        "long_attempts": attempts,
        "long_conversions": conversions,
        "long_conv_rate": (conversions / attempts) if attempts else 0.0,
    }
