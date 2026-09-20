import json
import time

from engine.get_schedule import (
    get_schedule,
    TokenExpired,
)
from engine.get_token import get_token

from logger import logger as log


SETTINGS_FILE = "./data/settings.json"

INTERVAL = 60
RETRY_INTERVAL = 10


def get_interval():
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            settings = json.load(file)

        interval = settings.get(
            "update_frequency",
            INTERVAL,
        )

        interval = int(interval)

        if interval > 0:
            return interval

    except Exception as error:
        log.error(
            f"Failed to read update frequency: {error}"
        )

    return INTERVAL


def run_schedule_cycle(on_schedule_updated=None):
    log.info("Schedule monitoring started")

    while True:
        try:
            log.info("< Initialising schedule update >")

            get_schedule()

            if on_schedule_updated:
                on_schedule_updated()

            interval = get_interval()

            log.info(f"[Next schedule update in {interval} seconds]")

            time.sleep(interval)

        except TokenExpired:
            log.warning("Authentication token expired")

            log.info(
                "Refreshing authentication token"
            )

            try:
                get_token()

                log.info(
                    "Authentication token refreshed successfully"
                )

            except Exception as error:
                log.error(
                    f"Failed to refresh authentication token: {error}"
                )

                log.info(
                    f"Retrying authentication in {RETRY_INTERVAL} seconds"
                )

                time.sleep(RETRY_INTERVAL)

        except Exception as error:
            log.error(
                f"Failed to update schedule: {error}"
            )

            log.info(
                f"Retrying schedule update in {RETRY_INTERVAL} seconds"
            )

            time.sleep(RETRY_INTERVAL)


if __name__ == "__main__":
    run_schedule_cycle()