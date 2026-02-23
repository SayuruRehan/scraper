from __future__ import annotations

import time
from pathlib import Path

import schedule

from src.orchestrator import run_pipeline


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent

    def job() -> None:
        output = run_pipeline(project_root)
        print(f"Daily run exported: {output}")

    schedule.every().day.at("02:00").do(job)
    print("Scheduler started. Daily run at 02:00 local time.")

    while True:
        schedule.run_pending()
        time.sleep(30)
