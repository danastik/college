import json
import webbrowser

from logger import logger as log


SETTINGS_FILE = "./data/settings.json"


def open_ktalk(lesson):
    log.info("KTalk open request received")

    try:
        with open(
            SETTINGS_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            settings = json.load(file)

    except Exception as error:
        log.error(
            f"Failed to load settings for KTalk: {error}"
        )
        return

    if not settings.get(
        "auto_open_ktalk",
        False,
    ):
        log.info(
            "Automatic KTalk opening is disabled"
        )
        return

    link = lesson.get("ссылка")

    if not link:
        log.warning(
            "KTalk link is missing for the lesson"
        )
        return

    log.info("Opening KTalk link")

    try:
        result = webbrowser.open(link)

        log.info(
            f"KTalk link open request completed: {result}"
        )

    except Exception as error:
        log.error(
            f"Failed to open KTalk link: {error}"
        )