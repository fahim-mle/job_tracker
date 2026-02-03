import logging
from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
import requests

from src.scrapers.linkedin import LinkedInScraper


def _make_text_node(text: str) -> AsyncMock:
    node = AsyncMock()
    node.text_content.return_value = text
    return node


def _make_attr_node(value: str) -> AsyncMock:
    node = AsyncMock()
    node.get_attribute.return_value = value
    return node


@pytest.mark.asyncio
async def test_scrape_parses_linkedin_job_cards(monkeypatch):
    scraper = LinkedInScraper(requests.Session(), logging.getLogger("test_linkedin"))
    monkeypatch.setattr(scraper, "_wait_for_rate_limit", AsyncMock())
    monkeypatch.setattr(scraper, "_handle_cookie_consent", AsyncMock())

    title_node = _make_text_node("Python Developer")
    company_node = _make_text_node("Tech Corp")
    location_node = _make_text_node("Remote")
    time_node = _make_text_node("2 days ago")
    link_node = _make_attr_node("https://linkedin.com/jobs/view/123")

    card = AsyncMock()

    def card_query_selector(selector: str):
        mapping = {
            "h3.base-search-card__title": title_node,
            "h4.base-search-card__subtitle": company_node,
            ".job-search-card__location": location_node,
            "time": time_node,
            "a.base-card__full-link": link_node,
        }
        return mapping.get(selector)

    card.query_selector.side_effect = card_query_selector

    empty_card = AsyncMock()

    def empty_query_selector(selector: str):
        if selector in {"h3.base-search-card__title", "h3"}:
            return None
        return None

    empty_card.query_selector.side_effect = empty_query_selector

    page = AsyncMock()
    page.query_selector_all.return_value = [card, empty_card]
    browser = AsyncMock()
    browser.new_page.return_value = page

    chromium = SimpleNamespace(launch=AsyncMock(return_value=browser))
    playwright_instance = SimpleNamespace(chromium=chromium)

    async_context = AsyncMock()
    async_context.__aenter__.return_value = playwright_instance
    async_context.__aexit__.return_value = None

    monkeypatch.setattr("src.scrapers.linkedin.async_playwright", lambda: async_context)

    results = await scraper.scrape({"keywords": "python", "location": "remote"})

    assert results == [
        {
            "title": "Python Developer",
            "company": "Tech Corp",
            "location": "Remote",
            "date_posted": date.today() - timedelta(days=2),
            "url": "https://linkedin.com/jobs/view/123",
        }
    ]
    browser.close.assert_awaited_once()


def test_parse_job_date_relative_values():
    scraper = LinkedInScraper(requests.Session(), logging.getLogger("test_dates"))

    assert scraper._parse_job_date("2 days ago") == date.today() - timedelta(days=2)
    assert scraper._parse_job_date("1 week ago") == date.today() - timedelta(days=7)
    assert scraper._parse_job_date("Just now") == date.today()
