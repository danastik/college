import json
import os
import threading

from engine.schedule_get_cycle import run_schedule_cycle
from app import run_app, ScheduleUpdateNotifier
from logger import logger


os.chdir(os.path.dirname(os.path.abspath(__file__)))


SETTINGS_FILE = "./data/settings.json"


def load_settings():
    with open(
        SETTINGS_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main():
    logger.info("Application started")

    try:
        settings = load_settings()
        logger.info("Settings loaded successfully")

    except Exception as error:
        logger.error(
            f"Failed to load settings: {error}"
        )
        raise

    notifier = ScheduleUpdateNotifier()

    schedule_thread = threading.Thread(
        target=run_schedule_cycle,
        args=(notifier.updated.emit,),
        daemon=True,
    )

    schedule_thread.start()

    logger.info(
        "Schedule update thread started"
    )

    run_app(
        notifier,
        settings,
    )


if __name__ == "__main__":
    main()