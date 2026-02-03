from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Mapping
from urllib.parse import quote_plus

from playwright.async_api import async_playwright

from src.scrapers.base import BaseScraper


class LinkedInScraper(BaseScraper):
    async def scrape(self, params: Mapping[str, Any]) -> list[dict[str, Any]]:
        keywords = params.get("keywords")
        location = params.get("location")

        if not keywords or not location:
            raise ValueError("params must include 'keywords' and 'location'")

        await self._wait_for_rate_limit(1.0, 3.0)

        search_url = (
            "https://www.linkedin.com/jobs/search?"
            f"keywords={quote_plus(str(keywords))}&location={quote_plus(str(location))}"
        )

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(search_url, wait_until="domcontentloaded")
                await self._handle_cookie_consent(page)
                try:
                    await page.wait_for_selector("div.base-card", timeout=10000)
                except Exception:
                    self.logger.info("LinkedIn scraper: no job cards found")
                cards = await page.query_selector_all("div.base-card")
                results = [await self._parse_card(card) for card in cards]
            finally:
                await browser.close()

        return [item for item in results if item["title"]]

    async def _handle_cookie_consent(self, page: Any) -> None:
        try:
            selectors = [
                "button:has-text('Accept cookies')",
                "button:has-text('Accept')",
                "button:has-text('Agree')",
            ]
            for selector in selectors:
                locator = page.locator(selector)
                if await locator.count() > 0:
                    await locator.first.click(timeout=2000)
                    return
        except Exception:
            return

    async def _parse_card(self, card: Any) -> dict[str, Any]:
        title = await self._get_text(card, "h3.base-search-card__title")
        if not title:
            title = await self._get_text(card, "h3")

        company = await self._get_text(card, "h4.base-search-card__subtitle")
        if not company:
            company = await self._get_text(card, "h4")

        location = await self._get_text(card, ".job-search-card__location")
        date_text = await self._get_text(card, "time")
        url = await self._get_attribute(card, "a.base-card__full-link", "href")

        return {
            "title": title,
            "company": company,
            "location": location,
            "date_posted": self._parse_job_date(date_text) if date_text else None,
            "url": url,
        }

    async def _get_text(self, element: Any, selector: str) -> str | None:
        node = await element.query_selector(selector)
        if not node:
            return None
        text = await node.text_content()
        if not text:
            return None
        cleaned = " ".join(text.split())
        return cleaned or None

    async def _get_attribute(
        self, element: Any, selector: str, attribute: str
    ) -> str | None:
        node = await element.query_selector(selector)
        if not node:
            return None
        value = await node.get_attribute(attribute)
        if not value:
            return None
        return value.strip() or None

    def _parse_job_date(self, date_text: str) -> date | str:
        cleaned = date_text.strip().lower()
        if cleaned == "just now":
            return date.today()
        if cleaned.endswith("ago"):
            tokens = cleaned.split()
            if len(tokens) >= 2 and tokens[0].isdigit():
                amount = int(tokens[0])
                if "day" in tokens[1]:
                    return date.today() - timedelta(days=amount)
                if "hour" in tokens[1]:
                    return date.today()
                if "week" in tokens[1]:
                    return date.today() - timedelta(days=amount * 7)
        return date_text
