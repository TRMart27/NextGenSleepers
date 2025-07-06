'''
implements global HTTP session, rety method,
polite requests, respecting PFR robots.txt
'''


import time
import random
import logging

from collections import deque
from typing import Deque
from typing import Dict
from typing import Any

import requests
from urllib3.util.retry import Retry

import config

#get mesa a logger !
logger = logging.getLogger(__name__)

class HttpClient:
    '''
    Respectful HTTP helper that's reusable
    '''

    _recent_calls: Deque[float]

    def __init__(self,
                 cooldown: int,
                 jail_time: int,
                 max_requests: int,
                 session: requests.Session = None):

        self.cooldown = cooldown
        self.jail_time = jail_time
        self.max_requests = max_requests

        self._recent_calls = deque(maxlen=max_requests)
        self.session = session or requests.Session()

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
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.session.headers.update({"User-Agent": config.USER_AGENT})


# ---- HTTP request implementations ----
    def send_request(self, request_url: str,
                     *, headers: Dict[str, str] = None,
                        params: Dict[str, Any] = None ):
        self._respect_limit()

        print(headers, params)
        #be weird
        time.sleep(random.uniform(1.87, 2.84))
        #now go
        response = self.session.get(request_url, timeout=(4, 10))
        if response.status_code == 429:
            print(f"\t\t\t[DEBUG | HttpClient] 429 Received URL => {request_url}")

        response.raise_for_status()
        return response



    def _respect_limit(self) -> None:
        time_stamp = time.time()

        #just add and return
        if len(self._recent_calls) < self.max_requests:
            self._recent_calls.appendleft(time_stamp)
            return

        oldest_call = self._recent_calls[-1]
        difference = time_stamp - oldest_call
        #check cooldown

        if difference < self.cooldown:
            throttle_time = self.cooldown - difference
            logger.debug(f"[DEBUG] Throttling for {throttle_time:.2f}")
            time.sleep(throttle_time)

            #update timestamp after sleeping
            time_stamp = time.time()

        self._recent_calls.appendleft(time_stamp)



    #python OOP context management
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        return False

# ---- Singleton structure ----
_client = None

def get_client() -> HttpClient:
    global _client
    if _client is None:
        _client = HttpClient(cooldown=config.REQUEST_COOLDOWN,
                             jail_time=config.REQUEST_JAIL,
                             max_requests=config.REQUEST_MAX)
    return _client


