import json
import requests

from datetime import datetime, timedelta

from logger import logger


API_URL = "https://app-api.rameevcollege.ru/api/widget/events-student"
AUTH_FILE = "./data/auth.json"
SCHEDULE_FILE = "./data/schedule.json"


class TokenExpired(Exception):
    pass


def get_token_from_auth():
    try:
        with open(
            AUTH_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            auth = json.load(file)

        token = auth["token"]

        if not token.startswith("Bearer "):
            token = f"Bearer {token}"

        return token

    except Exception as error:
        logger.error(
            f"Failed to load authentication data: {error}"
        )
        raise


def get_events():
    token = get_token_from_auth()

    now = datetime.now().astimezone()

    start = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    end = start + timedelta(days=7) - timedelta(milliseconds=1)

    try:
        response = requests.get(
            API_URL,
            params={
                "dateStart": start.isoformat(
                    timespec="milliseconds"
                ),
                "dateEnd": end.isoformat(
                    timespec="milliseconds"
                ),
            },
            headers={
                "Authorization": token,
                "Accept": "application/json",
            },
        )

    except requests.RequestException as error:
        logger.error(
            f"Schedule request failed: {error}"
        )
        raise

    logger.info(
        f"Schedule request completed with HTTP {response.status_code}"
    )

    if response.status_code == 401:
        raise TokenExpired(
            "Authentication token expired or invalid"
        )

    response.raise_for_status()

    return response.json()


def format_teacher(teacher):
    if not teacher:
        return None

    return " ".join(
        filter(
            None,
            [
                teacher.get("lastName"),
                teacher.get("firstName"),
                teacher.get("middleName"),
            ],
        )
    )


def format_event(event):
    props = event["eventProps"]

    subject = None
    lessons = []

    if props["type"] == "LESSON":
        program = props.get("program")

        if program:
            subject = program.get("name")

        for lesson in props.get("lessons") or []:
            if lesson.get("name"):
                lessons.append(lesson["name"])

    return {
        "id": event.get("id"),
        "начало": event.get("dateTimeStart"),
        "тип": props.get("type"),
        "продолжительность": props.get("duration"),
        "предмет": subject,
        "занятия": lessons,
        "преподаватель": format_teacher(
            props.get("teacher")
        ),
        "описание": props.get("description"),
        "ссылка": props.get("zoomLink"),
    }


def save_schedule(events):
    schedule = [
        format_event(event)
        for event in events
    ]

    try:
        with open(
            SCHEDULE_FILE,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                schedule,
                file,
                ensure_ascii=False,
                indent=4,
            )

    except Exception as error:
        logger.error(
            f"Failed to save schedule: {error}"
        )
        raise

    return schedule


def get_schedule():
    events = get_events()

    logger.info(
        f"Received {len(events)} schedule events"
    )

    schedule = save_schedule(events)

    logger.info(
        f"Schedule saved successfully: {len(schedule)} events"
    )

    return schedule