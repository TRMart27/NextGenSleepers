"""
implements global HTTP session, retry method,
polite requests, respecting PFR robots.txt
"""

import time
import random
import logging

from collections import deque
from typing import Deque, Dict, Any, Tuple

import requests
from requests.exceptions import HTTPError
from urllib3.util.retry import Retry

from src import config

# get mesa a logger !
logger = logging.getLogger(__name__)


class HttpClient:
    """
    Respectful HTTP helper that's reusable
    """

    def __init__(
        self,
        cooldown: float,
        jail_time: float,
        max_requests: int,
        session: requests.Session = None,
    ):

        self.cooldown = cooldown
        self.jail_time = jail_time
        self.max_requests = max_requests

        self._recent_calls: Deque[float] = deque(maxlen=max_requests)
        self._session: requests.Session = session or requests.Session()

        retry = Retry(
            total=config.MAX_RETIRES,
            connect=config.MAX_RETIRES,
            read=config.MAX_RETIRES,
            backoff_factor=config.BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
            raise_on_status=False,
            respect_retry_after_header=True,
        )

        adapter = requests.adapters.HTTPAdapter(max_retries=retry)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)
        self._session.headers.update({
            "User-Agent": config.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.pro-football-reference.com/",
            "Connection": "keep-alive",
        })

    # ---- HTTP request implementations ----
    def send_request(
        self,
        request_url: str,
        *,
        headers: Dict[str, str] = None,
        params: Dict[str, Any] = None,
        timeout: Tuple[float] = (4.0, 10.0),
    ):
        self._respect_limit()

        # be weird
        time.sleep(random.uniform(0.0, 0.2))
        # now go
        response = self._session.get(
            request_url, params=params, headers=headers, timeout=timeout
        )

        if response.status_code == 429:
            logger.debug(
                f"429 for {request_url}, sleeping {self.jail_time} then retrying"
            )
            time.sleep(self.jail_time)
            response = self._session.get(
                request_url, params=params, headers=headers, timeout=timeout
            )

        try:
            response.raise_for_status()
        except HTTPError:
            logger.debug(
                f"HTTP Error {response.status_code} for {request_url}: {response.text}"
            )
            raise

        return response

    def _respect_limit(self) -> None:
        time_stamp = time.monotonic()

        # just add and return
        if len(self._recent_calls) < self.max_requests:
            self._recent_calls.appendleft(time_stamp)
            return

        oldest_call = self._recent_calls[-1]
        difference = time_stamp - oldest_call
        # check cooldown

        if difference < self.cooldown:
            throttle_time = self.cooldown - difference
            logger.debug(f"[DEBUG] Throttling for {throttle_time:.2f}")
            time.sleep(throttle_time)

            # update timestamp after sleeping
            time_stamp = time.monotonic()

        self._recent_calls.appendleft(time_stamp)

    # python OOP context management
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()


def get_client(
    *,
    cooldown: float = config.REQUEST_COOLDOWN,
    jail_time: float = config.REQUEST_JAIL,
    max_requests: int = config.REQUEST_MAX,
) -> HttpClient:

    return HttpClient(cooldown=cooldown, jail_time=jail_time, max_requests=max_requests)
