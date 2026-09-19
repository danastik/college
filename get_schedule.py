import json
import requests

from datetime import datetime, timedelta


API_URL = "https://app-api.rameevcollege.ru/api/widget/events-student"
AUTH_FILE = "auth.json"
SCHEDULE_FILE = "schedule.json"


class TokenExpired(Exception):
    pass


def get_token_from_auth():
    with open(AUTH_FILE, "r", encoding="utf-8") as file:
        auth = json.load(file)

    token = auth["token"]

    if not token.startswith("Bearer "):
        token = f"Bearer {token}"

    return token


def get_events():
    token = get_token_from_auth()

    now = datetime.now().astimezone()

    start = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    ) -timedelta(days=3)

    end = start + timedelta(days=7) - timedelta(milliseconds=1)

    response = requests.get(
        API_URL,
        params={
            "dateStart": start.isoformat(timespec="milliseconds"),
            "dateEnd": end.isoformat(timespec="milliseconds"),
        },
        headers={
            "Authorization": token,
            "Accept": "application/json",
        },
    )

    print("HTTP:", response.status_code)

    # Именно 401 означает, что нужно получать новый токен
    if response.status_code == 401:
        raise TokenExpired("Токен недействителен или истёк")

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
        "преподаватель": format_teacher(props.get("teacher")),
        "описание": props.get("description"),
        "ссылка": props.get("zoomLink"),
    }


def save_schedule(events):
    schedule = [
        format_event(event)
        for event in events
    ]

    with open(SCHEDULE_FILE, "w", encoding="utf-8") as file:
        json.dump(
            schedule,
            file,
            ensure_ascii=False,
            indent=4,
        )

    return schedule


def get_schedule():
    events = get_events()

    print(f"Всего событий: {len(events)}")

    schedule = save_schedule(events)

    print(f"Записано в schedule.json: {len(schedule)}")

    return schedule