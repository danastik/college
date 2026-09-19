import threading

from schedule_get_cycle import run_schedule_cycle


def main():
    schedule_thread = threading.Thread(
        target=run_schedule_cycle,
        # daemon=True
    )
    schedule_thread.start()

    print("Основная программа запущена")
    print("Цикл обновления расписания запущен в отдельном потоке")

if __name__ == "__main__":
    main()