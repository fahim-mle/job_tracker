import asyncio
import logging
import requests

from src.scrapers.linkedin import LinkedInScraper


async def main():
    logger = logging.getLogger("test_scraper")
    logging.basicConfig(level=logging.INFO)
    session = requests.Session()

    scraper = LinkedInScraper(session=session, logger=logger)
    print("Starting scrape...")
    results = await scraper.scrape(
        {"keywords": "software engineer", "location": "Brisbane", "limit": 1}
    )

    if not results:
        print("No results found.")
        return

    first = results[0]
    print(f"Title: {first.get('title')}")
    desc = first.get("description")

    if desc:
        print(f"Description length: {len(desc)}")
        print(f"Snippet: {desc[:100]}...")
        assert len(desc) > 50
        print("SUCCESS: Description found and length > 50")
    else:
        print("FAILURE: Description is None")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
