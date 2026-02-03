from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

import requests

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.automation.scheduler import JobScheduler
from src.ai.llm_client import LLMClient
from src.database.session import SessionLocal
from src.logger import get_logger
from src.scrapers.linkedin import LinkedInScraper
from src.services.job_service import JobService
from src.services.skill_service import SkillService


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run scheduled LinkedIn scraping.")
    parser.add_argument(
        "--now",
        action="store_true",
        help="Run the scraping task immediately before scheduling.",
    )
    parser.add_argument("--hour", type=int, default=8, help="Daily run hour.")
    parser.add_argument("--minute", type=int, default=0, help="Daily run minute.")
    parser.add_argument("--keywords", default="Python", help="Search keywords.")
    parser.add_argument("--location", default="Remote", help="Search location.")
    return parser.parse_args()


async def main() -> None:
    args = _parse_args()
    logger = get_logger("run_scraper")
    db_session = SessionLocal()
    request_session = requests.Session()
    job_service = JobService(db_session)
    scraper = LinkedInScraper(request_session, logger)
    scheduler = JobScheduler()

    async def run_scraping_task() -> None:
        logger.info("Starting LinkedIn scraping run")
        try:
            results = await scraper.scrape(
                {"keywords": args.keywords, "location": args.location}
            )
            logger.info("Scraped %s job cards", len(results))
            for index, result in enumerate(results, start=1):
                company = result.get("company")
                title = result.get("title")
                if not company or not title:
                    logger.warning("Skipping job card missing company/title")
                    continue

                payload = {
                    "company": company,
                    "title": title,
                    "location": result.get("location"),
                    "posted_date": result.get("date_posted"),
                    "url": result.get("url"),
                    "source_platform": "linkedin",
                }
                job_service.upsert_job(payload)
                logger.info(
                    "Upserted job %s/%s: %s",
                    index,
                    len(results),
                    result.get("title"),
                )
            llm_client = LLMClient()
            skill_service = SkillService(db_session, llm_client)
            logger.info("Starting AI processing for new jobs")
            processed = job_service.process_new_jobs_with_ai(skill_service)
            logger.info("AI processing complete: %s jobs processed", processed)
            db_session.commit()
            logger.info("LinkedIn scraping run complete")
        except Exception:
            logger.exception("LinkedIn scraping run failed")
            db_session.rollback()

    try:
        if args.now:
            await run_scraping_task()

        scheduler.add_daily_job(run_scraping_task, hour=args.hour, minute=args.minute)
        scheduler.start()
        logger.info("Scheduler started: daily at %02d:%02d", args.hour, args.minute)
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Shutdown requested")
    finally:
        scheduler.stop()
        request_session.close()
        db_session.close()


if __name__ == "__main__":
    asyncio.run(main())
