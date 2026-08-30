#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: scheduler.py
Author: Maria Kevin
Created: 2026-08-27
Description: AsyncIOScheduler singleton for invite expiry kicks.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"


from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger
from pyrogram.client import Client

from service import invite_service

_KICK_EXPIRED_JOB_ID = "kick_expired"
_STARTUP_DELAY = timedelta(seconds=10)


class AppScheduler:
    """Owns the process-wide AsyncIOScheduler for background jobs."""

    def __init__(self) -> None:
        self._scheduler = AsyncIOScheduler()
        self._client: Client | None = None

    def start(self, client: Client) -> None:
        """Start the scheduler and register the hourly kick_expired job.

        Schedules a first run shortly after startup so short-lived memberships
        are not stuck waiting a full hour after a restart; then every hour.
        """
        self._client = client
        if self._scheduler.running:
            logger.warning("APScheduler already running; skipping start")
            return

        first_run = datetime.now(timezone.utc) + _STARTUP_DELAY
        self._scheduler.add_job(
            self._run_kick_expired,
            trigger=IntervalTrigger(hours=1),
            id=_KICK_EXPIRED_JOB_ID,
            replace_existing=True,
            next_run_time=first_run,
            coalesce=True,
            max_instances=1,
        )
        self._scheduler.start()
        logger.bind(
            job_id=_KICK_EXPIRED_JOB_ID,
            first_run=first_run.isoformat(),
            interval_hours=1,
        ).info("APScheduler started with hourly kick_expired job")

    async def _run_kick_expired(self) -> None:
        """Run invite_service.kick_expired against the stored bot client."""
        if self._client is None:
            logger.error("kick_expired job skipped: bot client not set")
            return
        logger.info("Scheduler firing kick_expired job")
        await invite_service.kick_expired(self._client)

    def shutdown(self) -> None:
        """Shut down the scheduler cleanly if it is running."""
        if not self._scheduler.running:
            logger.debug("APScheduler was not running; nothing to shut down")
            return
        self._scheduler.shutdown(wait=False)
        logger.info("APScheduler shut down")


app_scheduler = AppScheduler()
