"""
Run document sync on a schedule (in-process).

Prefer OS cron / Windows Task Scheduler for production; APScheduler is fine for
local demos and long-running containers.
"""

from __future__ import annotations

import logging
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler

from services.document_fetcher import DocumentFetcher
from services.regulatory_catalog import REGULATORY_SOURCES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def job_sync_regulatory_corpus() -> None:
    root = Path(__file__).resolve().parent
    data_dir = root / "data"
    with DocumentFetcher(data_dir) as fetcher:
        for result in fetcher.sync_all(REGULATORY_SOURCES):
            logger.info(
                "%s | http=%s changed=%s path=%s",
                result.doc_id,
                result.http_status,
                result.changed,
                result.path,
            )


def main() -> None:
    scheduler = BlockingScheduler()
    scheduler.add_job(
        job_sync_regulatory_corpus,
        "interval",
        hours=24,
        id="regulatory_corpus",
    )
    job_sync_regulatory_corpus()
    scheduler.start()


if __name__ == "__main__":
    main()
