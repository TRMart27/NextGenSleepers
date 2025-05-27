'''
implements global HTTP session, rety method,
polite requests, respecting PFR robots.txt
'''


import time
import random
import logging

from collections import deque
from typing import Deque

import requests
from urllib3.util.retry import Retry

from .. import config

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
            total=config.MAX_RETRIES,
            connect=config.MAX_RETRIES,
            read=config.MAX_RETRIES,
            backoff_factor=config.BACKOFF_FACTOR,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
            raise_on_status=False,
        )

        adapter = requests.adapters.HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.session.headers.update({"User-Agent": config.USER_AGENT})


# ---- HTTP request implementations ----
    def send_request(self, request_url: str):
        self._respect_limit()

        #be weird
        time.sleep(random.uniform(1.27, 2.84))
        #now go
        response = self.session.get(request_url, timeout=(4, 10))
        if response.status_code == 429:
            logger.warning(f"[HTTPClient] 429 Received - sleeping through jail {self.jail_time}")
            time.sleep(self.jail_time)

            #try again
            response = self.session.get(request_url)

        response.raise_for_status()
        return response



    def _respect_limit(self):
        time_stamp = time.time()
        time_since_head = time_stamp - self.jail_time

        if len(self._recent_calls) == self.max_requests and time_since_head < self.cooldown:
            wait_time = self.cooldown - time_since_head
            logger.debug(f"[INFO - HTTPClient] Throttling... ({wait_time})")
            time.sleep(wait_time)

        time_stamp = time.time()
        self._recent_calls.append(time_stamp)


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
        _client = HttpClient()
    return _client


