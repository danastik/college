import json
from datetime import datetime, timezone

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
    QPushButton,
)


SCHEDULE_FILE = "schedule.json"

DAYS = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресенье",
]


class LessonCard(QFrame):
    def __init__(self, lesson):
        super().__init__()

        self.start_time = datetime.fromisoformat(
            lesson["начало"].replace("Z", "+00:00")
        )

        self.duration_minutes = lesson.get(
            "продолжительность",
            45,
        )

        if lesson.get("тип") == "EVENT":
            self.subject = "Особая встреча"
        else:
            self.subject = lesson["предмет"]

        self.setObjectName("lessonCard")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 12, 15, 12)
        layout.setSpacing(15)

        # Цветной индикатор типа занятия
        self.type_indicator = QFrame()
        self.type_indicator.setFixedWidth(6)
        self.type_indicator.setObjectName(
            self.get_type_color(lesson)
        )

        # Время
        self.time_label = QLabel(
            self.start_time.astimezone().strftime("%H:%M")
        )
        self.time_label.setObjectName("lessonTime")

        # Предмет
        self.subject_label = QLabel(self.subject)
        self.subject_label.setObjectName("lessonSubject")

        # Оставшееся / прошедшее время
        self.remaining_label = QLabel()
        self.remaining_label.setObjectName("lessonRemaining")

        layout.addWidget(self.type_indicator)
        layout.addWidget(self.time_label)
        layout.addWidget(self.subject_label)

        layout.addStretch()

        layout.addWidget(self.remaining_label)

        self.update_remaining()

    @staticmethod
    def get_type_color(lesson):
        if lesson.get("тип") == "EVENT":
            return "special"

        description = lesson.get("описание")

        if description == "Встреча с преподавателем":
            return "lesson"

        if description == "Работа на платформе":
            return "practice"

        return "lesson"

    def update_remaining(self):
        now = datetime.now(timezone.utc)

        difference = self.start_time - now
        total_seconds = int(difference.total_seconds())

        # Урок уже начался
        if total_seconds <= 0:

            elapsed_seconds = int(
                (now - self.start_time).total_seconds()
            )

            # Урок закончился
            if elapsed_seconds >= self.duration_minutes * 60:
                self.remaining_label.setText(
                    "Урок закончился"
                )
                return

            # Урок идёт
            elapsed_minutes = elapsed_seconds // 60

            self.remaining_label.setText(
                f"Начался {elapsed_minutes} мин. назад"
            )
            return

        # Урок ещё не начался

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
                text = (
                    f"Через {total_hours} ч. "
                    f"{minutes} мин."
                )
            else:
                text = f"Через {total_hours} ч."

            self.remaining_label.setText(text)
            return

        # 24 часа и больше
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
        main_layout.setSpacing(10)

        # Расписание
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        self.content = QWidget()

        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setSpacing(8)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        scroll.setWidget(self.content)

        main_layout.addWidget(scroll)

        # Нижняя информационная панель
        info_frame = QFrame()
        info_frame.setObjectName("scheduleInfo")

        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(10, 8, 10, 8)
        info_layout.setSpacing(10)

        # Ближайший урок
        self.next_lesson_label = QLabel()
        self.next_lesson_label.setObjectName("nextLesson")

        self.next_lesson_label.setOpenExternalLinks(True)
        self.next_lesson_label.setTextFormat(Qt.RichText)

        info_layout.addWidget(
            self.next_lesson_label
        )

        info_layout.addStretch()

        # Легенда цветов
        legend = QHBoxLayout()
        legend.setSpacing(3)
        legend.setContentsMargins(0, 0, 0, 0)

        lesson_legend = QLabel("🔵 Урок")
        lesson_legend.setObjectName("lessonLegend")

        practice_legend = QLabel("🟢 Практическая")
        practice_legend.setObjectName("practiceLegend")

        special_legend = QLabel("🟡 Особая встреча")
        special_legend.setObjectName("specialLegend")

        legend.addWidget(lesson_legend)
        legend.addWidget(practice_legend)
        legend.addWidget(special_legend)

        info_layout.addLayout(legend)

        # Кнопка +
        self.add_button = QPushButton("➕")
        self.add_button.setObjectName("addButton")
        self.add_button.setFixedSize(36, 36)
        self.add_button.setCursor(Qt.PointingHandCursor)

        info_layout.addWidget(self.add_button)

        main_layout.addWidget(info_frame)

        self.load_schedule()

        # Обновляем время каждую секунду
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_schedule)
        self.timer.start(1000)

    def clear_schedule(self):
        self.cards.clear()

        while self.content_layout.count():
            item = self.content_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def reload_schedule(self):
        self.load_schedule()

    def load_schedule(self):
        self.clear_schedule()

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

        # Сортируем занятия по времени начала
        schedule.sort(
            key=lambda lesson: lesson["начало"]
        )

        current_date = None

        for lesson in schedule:
            start_time = datetime.fromisoformat(
                lesson["начало"].replace("Z", "+00:00")
            )

            local_date = start_time.astimezone().date()

            # Новый день
            if local_date != current_date:
                current_date = local_date

                day_name = DAYS[local_date.weekday()]

                day_label = QLabel(
                    f"{day_name}, "
                    f"{local_date.strftime('%d.%m.%Y')}"
                )

                day_label.setObjectName("dayHeader")

                self.content_layout.addWidget(
                    day_label
                )

            card = LessonCard(lesson)

            # Сохраняем исходные данные
            card.lesson_data = lesson

            self.cards.append(card)
            self.content_layout.addWidget(card)

        self.content_layout.addStretch()

        self.update_schedule()

    def update_next_lesson(self):
        now = datetime.now(timezone.utc)

        closest_card = None
        closest_difference = None

        for card in self.cards:
            difference = (
                card.start_time - now
            ).total_seconds()

            # Только будущие занятия
            # и только те, что начнутся в ближайшие 15 минут
            if 0 < difference <= 15 * 60:

                if (
                    closest_difference is None
                    or difference < closest_difference
                ):
                    closest_card = card
                    closest_difference = difference

        if closest_card is None:
            self.next_lesson_label.setText(
                "В ближайшие 15 минут занятий нет"
            )
            return

        lesson = closest_card.lesson_data

        subject = closest_card.subject

        start_time = (
            closest_card.start_time
            .astimezone()
            .strftime("%H:%M")
        )

        link = lesson.get("ссылка")

        if link:
            text = (
                f"Следующий урок: "
                f'<a href="{link}">'
                f"{subject} ({start_time})"
                f"</a>"
            )
        else:
            text = (
                f"Следующий урок: "
                f"{subject} ({start_time})"
            )

        self.next_lesson_label.setText(text)

    def update_highlight(self):
        now = datetime.now(timezone.utc)

        current_card = None
        next_card = None

        # Ищем текущий урок
        for card in self.cards:
            if card.start_time <= now:

                elapsed_seconds = (
                    now - card.start_time
                ).total_seconds()

                if elapsed_seconds < (
                    card.duration_minutes * 60
                ):
                    if (
                        current_card is None
                        or card.start_time
                        > current_card.start_time
                    ):
                        current_card = card

        # Если текущего урока нет —
        # ищем ближайший будущий
        if current_card is None:
            for card in self.cards:
                if card.start_time > now:
                    if (
                        next_card is None
                        or card.start_time
                        < next_card.start_time
                    ):
                        next_card = card

        # Обновляем жёлтую обводку
        for card in self.cards:
            should_highlight = (
                card is current_card
                or (
                    current_card is None
                    and card is next_card
                )
            )

            card.setProperty(
                "highlighted",
                should_highlight,
            )

            card.style().unpolish(card)
            card.style().polish(card)

    def update_schedule(self):
        # Обновляем время у всех карточек
        for card in self.cards:
            card.update_remaining()
            card.setVisible(True)

        # Обновляем жёлтую обводку
        self.update_highlight()

        # Обновляем нижнюю информацию
        self.update_next_lesson()