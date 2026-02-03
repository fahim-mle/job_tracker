from __future__ import annotations

from collections.abc import Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler


class JobScheduler:
    def __init__(self) -> None:
        self._scheduler = AsyncIOScheduler()

    def start(self) -> None:
        self._scheduler.start()

    def add_daily_job(self, func: Callable, hour: int = 8, minute: int = 0) -> None:
        self._scheduler.add_job(func, "cron", hour=hour, minute=minute)

    def stop(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown()
