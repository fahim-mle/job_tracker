from __future__ import annotations

import asyncio
import logging
import random
from abc import ABC, abstractmethod
from typing import Any, Mapping

import requests


class BaseScraper(ABC):
    def __init__(self, session: requests.Session, logger: logging.Logger) -> None:
        self.session = session
        self.logger = logger

    @abstractmethod
    def scrape(self, params: Mapping[str, Any]) -> Any:
        raise NotImplementedError

    async def _sleep(self, seconds: float) -> None:
        delay = max(0.0, seconds)
        await asyncio.sleep(delay)

    def _get_random_delay(self, min_delay: float, max_delay: float) -> float:
        return random.uniform(min_delay, max_delay)

    async def _wait_for_rate_limit(
        self, min_delay: float, max_delay: float | None = None
    ) -> None:
        if max_delay is None:
            await self._sleep(min_delay)
            return

        delay = self._get_random_delay(min_delay, max_delay)
        await self._sleep(delay)

    async def _rate_limit(
        self, min_delay: float, max_delay: float | None = None
    ) -> None:
        await self._wait_for_rate_limit(min_delay, max_delay)
