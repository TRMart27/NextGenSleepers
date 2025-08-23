"""
implements global HTTP session, retry method,
polite requests, respecting PFR robots.txt
"""

import time
import random
import logging

from collections import deque
from typing import Deque, Dict, Any, Tuple

# import requests
# from requests.adapters import HTTPAdapter
# from requests.exceptions import HTTPError
from curl_cffi import requests as cf
from urllib3.util.retry import Retry

from src import config

# get mesa a logger !
logging.basicConfig(filename="NextGenSleepers.log", level=logging.DEBUG)
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
            session: cf.Session = None,
            *,
            http_version: str = "v2"
    ):

        self.cooldown = cooldown
        self.jail_time = jail_time
        self.max_requests = max_requests
        self.http_version = http_version

        self._recent_calls: Deque[float] = deque(maxlen=max_requests)
        self._session: cf.Session = session or cf.Session(
            impersonate="chrome",
            timeout=None,
        )

        self._max_retries = config.MAX_RETIRES
        self._backoff_factor = config.BACKOFF_FACTOR

    # ---- HTTP request implementations ----
    def send_request(
            self,
            request_url: str,
            *,
            headers: Dict[str, str] = None,
            params: Dict[str, Any] = None,
            timeout: float = 14.0,
    ):
        self._respect_limit()

        # be weird
        time.sleep(random.uniform(1.0, 3.2))

        attempt = 0
        while True:
            attempt += 1
            try:
                response = self._session.get(
                    request_url,
                    params=params,
                    headers=headers,
                    timeout=timeout,
                    http_version=self.http_version
                )

                if response.status_code == 429:
                    logger.debug(
                        f"429 for {request_url}, sleeping {self.jail_time} then retrying"
                    )
                    time.sleep(self.jail_time)

                if response.status_code == 403:
                    logger.debug(
                        f"403 for {request_url}:\n"
                        f"{response.text}"
                    )

                if response.status_code in (429, 500, 502, 503, 504):
                    if attempt < self._max_retries:
                        sleep_for = self._backoff(attempt)

                        logger.debug(f"[RETRY] {response.status_code} for {request_url}; sleeping {sleep_for} seconds")
                        time.sleep(sleep_for)
                        continue

                response.raise_for_status()
                return response

            except Exception as e:
                if attempt < self._max_retries:
                    sleep_for = self._backoff(attempt)
                    time.sleep(sleep_for)
                    continue
                logger.debug(f"giving up {type(e).__name__} on {request_url}")
                raise

    def _backoff(self, attempt: int) -> float:
        base = self._backoff_factor * (2 ** (attempt - 1))
        return base + random.uniform(0, base)

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
