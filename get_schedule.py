import json
import requests
from datetime import datetime, timedelta


API_URL = "https://app-api.rameevcollege.ru/api/widget/events-student"


# Загружаем токен
with open("auth.json", "r", encoding="utf-8") as f:
    auth = json.load(f)

TOKEN = auth["token"]

if not TOKEN.startswith("Bearer "):
    TOKEN = f"Bearer {TOKEN}"

    

print("Токен есть:", bool(TOKEN))
print("Начинается с Bearer:", TOKEN.startswith("Bearer "))
print("Длина токена:", len(TOKEN))


def get_events():
    now = datetime.now().astimezone()

    start = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    end = start + timedelta(days=7) - timedelta(milliseconds=1)

    response = requests.get(
        API_URL,
        params={
            "dateStart": start.isoformat(timespec="milliseconds"),
            "dateEnd": end.isoformat(timespec="milliseconds"),
        },
        headers={
            "Authorization": TOKEN,
            "Accept": "application/json",
        },
    )

    print("HTTP:", response.status_code)
    print("Ответ сервера:", response.text[:500])
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

    with open("schedule.json", "w", encoding="utf-8") as f:
        json.dump(
            schedule,
            f,
            ensure_ascii=False,
            indent=4,
        )

    return schedule


data = get_events()

print(f"Всего событий: {len(data)}")

schedule = save_schedule(data)

print(f"Получено событий: {len(data)}")
print(f"Записано в schedule.json: {len(schedule)}")