import json
import webbrowser

from logger import logger


SETTINGS_FILE = "./data/settings.json"


def open_ktalk(lesson):
    logger.info("KTalk open request received")

    try:
        with open(
            SETTINGS_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            settings = json.load(file)

    except Exception as error:
        logger.error(
            f"Failed to load settings for KTalk: {error}"
        )
        return

    if not settings.get(
        "auto_open_ktalk",
        False,
    ):
        logger.info(
            "Automatic KTalk opening is disabled"
        )
        return

    link = lesson.get("ссылка")

    if not link:
        logger.warning(
            "KTalk link is missing for the lesson"
        )
        return

    logger.info("Opening KTalk link")

    try:
        result = webbrowser.open(link)

        logger.info(
            f"KTalk link open request completed: {result}"
        )

    except Exception as error:
        logger.error(
            f"Failed to open KTalk link: {error}"
        )