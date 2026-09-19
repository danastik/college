import threading

from schedule_get_cycle import run_schedule_cycle
from app import run_app, ScheduleUpdateNotifier


def main():
    notifier = ScheduleUpdateNotifier()

    schedule_thread = threading.Thread(
        target=run_schedule_cycle,
        args=(notifier.updated.emit,),
        daemon=True,
    )

    schedule_thread.start()

    print("Основная программа запущена")
    print("Цикл обновления расписания запущен в отдельном потоке")

    run_app(notifier)


if __name__ == "__main__":
    main()