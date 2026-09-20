import time

from engine.get_schedule import get_schedule, TokenExpired
from engine.get_token import get_token


INTERVAL = 60
RETRY_INTERVAL = 10


def run_schedule_cycle(on_schedule_updated=None):
    print("Запуск мониторинга расписания...")

    while True:
        try:
            print("\nПолучаем расписание...")

            get_schedule()

            if on_schedule_updated:
                on_schedule_updated()

            print(f"Следующая проверка через {INTERVAL} секунд.")
            time.sleep(INTERVAL)

        except TokenExpired:
            print("Текущий токен недействителен.")
            print("Получаем новый токен...")

            try:
                get_token()
                print("Новый токен получен.")

            except Exception as e:
                print(f"Ошибка при получении токена: {e}")
                print(f"Повторяем через {RETRY_INTERVAL} секунд.")
                time.sleep(RETRY_INTERVAL)

        except Exception as e:
            print(f"Ошибка при получении расписания: {e}")
            print(f"Повторяем через {RETRY_INTERVAL} секунд.")
            time.sleep(RETRY_INTERVAL)


if __name__ == "__main__":
    run_schedule_cycle()