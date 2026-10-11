"""Official-API publishers only. No scraping, no unofficial clients, no automated follows, likes or comments:
those are what get new accounts restricted. Every publisher defaults to dry-run.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable

import requests


class PublishError(RuntimeError):
    pass


@dataclass
class Http:
    """Thin wrapper so tests can swap the network and the clock."""
    session: requests.Session = field(default_factory=requests.Session)
    sleep: Callable[[float], None] = time.sleep
    timeout: float = 30.0

    def get(self, url: str, **kw) -> dict:
        return self._json(self.session.get(url, timeout=self.timeout, **kw))

    def post(self, url: str, **kw) -> dict:
        return self._json(self.session.post(url, timeout=self.timeout, **kw))

    @staticmethod
    def _json(resp) -> dict:
        try:
            body = resp.json()
        except ValueError:
            body = {"raw": resp.text}
        if resp.status_code >= 400:
            raise PublishError(f"HTTP {resp.status_code}: {body}")
        return body
