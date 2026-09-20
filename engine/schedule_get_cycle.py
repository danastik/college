import json
import time

from engine.get_schedule import get_schedule, TokenExpired
from engine.get_token import get_token


SETTINGS_FILE = "./data/settings.json"

INTERVAL = 60
RETRY_INTERVAL = 10


def get_interval():
    try:
        with open(
            SETTINGS_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            settings = json.load(file)

        interval = settings.get(
            "update_frequency",
            INTERVAL,
        )

        interval = int(interval)

        if interval > 0:
            return interval

    except Exception as e:
        print(f"Ошибка чтения частоты обновления: {e}")

    return INTERVAL


def run_schedule_cycle(on_schedule_updated=None):
    print("Запуск мониторинга расписания...")

    while True:
        try:
            print("\nПолучаем расписание...")

            get_schedule()

            if on_schedule_updated:
                on_schedule_updated()

            interval = get_interval()

            print(
                f"Следующая проверка через {interval} секунд."
            )

            time.sleep(interval)

        except TokenExpired:
            print("Текущий токен недействителен.")
            print("Получаем новый токен...")

            try:
                get_token()
                print("Новый токен получен.")

            except Exception as e:
                print(
                    f"Ошибка при получении токена: {e}"
                )
                print(
                    f"Повторяем через {RETRY_INTERVAL} секунд."
                )
                time.sleep(RETRY_INTERVAL)

        except Exception as e:
            print(
                f"Ошибка при получении расписания: {e}"
            )
            print(
                f"Повторяем через {RETRY_INTERVAL} секунд."
            )
            time.sleep(RETRY_INTERVAL)


if __name__ == "__main__":
    run_schedule_cycle()