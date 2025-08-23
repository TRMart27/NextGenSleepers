import os
import logging

from src.config import CACHE_DIR


logger = logging.getLogger(__name__)
def html_page_path(year: int) -> str | None:
    return os.path.join(CACHE_DIR, "data", "raw", "pages", f"{year}.html")


def load_html(filepath: str) -> str:
    try:
        with open(filepath, "r", encoding="utf-8") as file_ref:
            html = file_ref.read()
            return html
    except Exception as e:
        logger.debug(f"An Unexpected Error has Occured: {e}")

def cache_html(filepath, content: str) -> None:
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)
            return
    except Exception as e:
        logger.debug(f"An Unexpected Error has Occured: {e}")
