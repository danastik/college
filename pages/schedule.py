import json
from datetime import datetime, timezone

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
)


SCHEDULE_FILE = "schedule.json"


class LessonCard(QFrame):
    def __init__(self, lesson):
        super().__init__()

        self.start_time = datetime.fromisoformat(
            lesson["начало"].replace("Z", "+00:00")
        )

        self.subject = lesson["предмет"]

        self.setObjectName("lessonCard")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(15)

        # Дата
        self.date_label = QLabel(
            self.start_time.astimezone().strftime("%d.%m.%Y")
        )
        self.date_label.setObjectName("lessonDate")

        # Время
        self.time_label = QLabel(
            self.start_time.astimezone().strftime("%H:%M")
        )
        self.time_label.setObjectName("lessonTime")

        # Предмет
        self.subject_label = QLabel(self.subject)
        self.subject_label.setObjectName("lessonSubject")

        # Оставшееся время
        self.remaining_label = QLabel()
        self.remaining_label.setObjectName("lessonRemaining")

        layout.addWidget(self.date_label)
        layout.addWidget(self.time_label)
        layout.addWidget(self.subject_label)

        layout.addStretch()

        layout.addWidget(self.remaining_label)

        self.update_remaining()

    def update_remaining(self):
        now = datetime.now(timezone.utc)

        difference = self.start_time - now
        total_seconds = int(difference.total_seconds())

        if total_seconds <= 0:
            self.remaining_label.setText("Урок уже начался")
            return

        # Меньше минуты — показываем секунды
        if total_seconds < 60:
            self.remaining_label.setText(
                f"Через {total_seconds} сек."
            )
            return

        total_minutes = total_seconds // 60

        # Меньше часа — показываем минуты
        if total_minutes < 60:
            self.remaining_label.setText(
                f"Через {total_minutes} мин."
            )
            return

        total_hours = total_minutes // 60
        minutes = total_minutes % 60

        # Меньше суток — показываем часы и минуты
        if total_hours < 24:
            if minutes > 0:
                text = f"Через {total_hours} ч. {minutes} мин."
            else:
                text = f"Через {total_hours} ч."

            self.remaining_label.setText(text)
            return

        # 24 часа и больше — показываем дни, часы и минуты
        days = total_hours // 24
        hours = total_hours % 24

        parts = [f"{days} д."]

        if hours > 0:
            parts.append(f"{hours} ч.")

        if minutes > 0:
            parts.append(f"{minutes} мин.")

        self.remaining_label.setText(
            "Через " + " ".join(parts)
        )


class SchedulePage(QWidget):
    def __init__(self):
        super().__init__()

        self.cards = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        self.content = QWidget()

        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setSpacing(8)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        scroll.setWidget(self.content)

        main_layout.addWidget(scroll)

        self.load_schedule()

        # Обновляем обратный отсчёт каждую секунду
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_remaining)
        self.timer.start(1000)

    def load_schedule(self):
        try:
            with open(
                SCHEDULE_FILE,
                "r",
                encoding="utf-8",
            ) as file:
                schedule = json.load(file)

        except Exception as e:
            error_label = QLabel(
                f"Не удалось загрузить расписание:\n{e}"
            )
            self.content_layout.addWidget(error_label)
            return

        for lesson in schedule:
            card = LessonCard(lesson)

            self.cards.append(card)
            self.content_layout.addWidget(card)

        self.content_layout.addStretch()

    def update_remaining(self):
        for card in self.cards:
            card.update_remaining()