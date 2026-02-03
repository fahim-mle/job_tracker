import logging
from unittest.mock import AsyncMock

import pytest
import requests

from src.scrapers import base as base_module
from src.scrapers.base import BaseScraper


class DummyScraper(BaseScraper):
    def scrape(self, params):
        return params


@pytest.mark.asyncio
async def test_wait_for_rate_limit_uses_min_delay(monkeypatch):
    scraper = DummyScraper(requests.Session(), logging.getLogger("test_scraper"))
    sleep_mock = AsyncMock()
    monkeypatch.setattr(base_module.asyncio, "sleep", sleep_mock)

    await scraper._wait_for_rate_limit(1.5)

    sleep_mock.assert_awaited_once_with(1.5)


@pytest.mark.asyncio
async def test_wait_for_rate_limit_uses_random_delay(monkeypatch):
    scraper = DummyScraper(requests.Session(), logging.getLogger("test_scraper_random"))
    sleep_mock = AsyncMock()
    monkeypatch.setattr(base_module.asyncio, "sleep", sleep_mock)
    monkeypatch.setattr(scraper, "_get_random_delay", lambda _min, _max: 2.5)

    await scraper._wait_for_rate_limit(1.0, 3.0)

    sleep_mock.assert_awaited_once_with(2.5)


def test_get_random_delay_uses_uniform(monkeypatch):
    scraper = DummyScraper(
        requests.Session(), logging.getLogger("test_scraper_uniform")
    )
    monkeypatch.setattr(base_module.random, "uniform", lambda _min, _max: 2.5)

    assert scraper._get_random_delay(1.0, 3.0) == 2.5
