import json
from datetime import datetime, timezone, timedelta
from uuid import uuid4
import ctypes
from ctypes import wintypes

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
    QPushButton,
    QDialog,
    QMessageBox,
)

from pages.add_event import AddEventDialog
from engine.notifications import NotificationManager
from engine.open_ktalk import open_ktalk
from logger import logger as log


SCHEDULE_FILE = "./data/schedule.json"
MANUAL_EVENTS_FILE = "./data/manual_events.json"

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

        return "special"

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
                self.remaining_label.setText("Урок закончился")
                return

            # Урок идёт
            elapsed_minutes = elapsed_seconds // 60

            self.remaining_label.setText(
                f"Начался {elapsed_minutes} мин. назад"
            )
            return

        # Урок ещё не начался

        # Меньше часа — показываем минуты и секунды
        if total_seconds < 60 * 60:
            total_minutes = total_seconds // 60
            seconds = total_seconds % 60

            if total_minutes > 0:
                self.remaining_label.setText(
                    f"Через {total_minutes} мин. "
                    f"{seconds:02d} сек."
                )
            else:
                self.remaining_label.setText(
                    f"Через {seconds} сек."
                )

            return

        total_minutes = total_seconds // 60

        # Меньше суток — показываем часы и минуты
        if total_minutes < 24 * 60:
            total_hours = total_minutes // 60
            minutes = total_minutes % 60

            if minutes > 0:
                text = (
                    f"Через {total_hours} ч. "
                    f"{minutes} мин."
                )
            else:
                text = f"Через {total_hours} ч."

            self.remaining_label.setText(text)
            return

def set_dark_title_bar(window):
    hwnd = int(window.winId())

    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    value = ctypes.c_int(1)

    ctypes.windll.dwmapi.DwmSetWindowAttribute(
        wintypes.HWND(hwnd),
        DWMWA_USE_IMMERSIVE_DARK_MODE,
        ctypes.byref(value),
        ctypes.sizeof(value),
    )

class SchedulePage(QWidget):
    def __init__(self, settings):
        super().__init__()

        self.cards = []
        self.started_lessons = set()

        self.notifications = NotificationManager(settings)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Расписание
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollBar:vertical {
                width: 8px;
                background: #606060;
                border-radius: 4px;
            }

            QScrollBar::handle:vertical {
                background: #222222;
                border-radius: 2px;
                min-height: 30px;
                margin: 0px 2px;
            }

            QScrollBar::handle:vertical:hover {
                background: #222222;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)

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

        self.add_button.clicked.connect(
            self.open_add_event_dialog
        )

        info_layout.addWidget(self.add_button)

        main_layout.addWidget(info_frame)

        self.load_schedule()

        # Обновляем время каждую секунду
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_schedule)
        self.timer.start(1000)

    def has_event_conflict(self, new_event):
        new_start = datetime.fromisoformat(
            new_event["начало"].replace("Z", "+00:00")
        )
        new_end = new_start.timestamp() + new_event["продолжительность"] * 60

        try:
            with open(SCHEDULE_FILE, "r", encoding="utf-8") as file:
                schedule = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            schedule = []

        schedule.extend(self.load_manual_events())

        for event in schedule:
            event_start = datetime.fromisoformat(
                event["начало"].replace("Z", "+00:00")
            )
            event_end = event_start.timestamp() + event.get("продолжительность", 45) * 60

            if (
                new_start.timestamp() < event_end
                and new_end > event_start.timestamp()
            ):
                return event

        return None

    def get_current_lesson(self):
        now = datetime.now(timezone.utc)

        for card in self.cards:
            start_time = card.start_time

            duration_minutes = card.duration_minutes

            end_time = (
                start_time.timestamp()
                + duration_minutes * 60
            )

            if (
                start_time.timestamp()
                <= now.timestamp()
                < end_time
            ):
                return card

        return None

    def clean_expired_events(self):
        now = datetime.now(timezone.utc)
        files = [SCHEDULE_FILE, MANUAL_EVENTS_FILE]
        removed_any = False

        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    events = json.load(file)

                cleaned_events = []

                for event in events:
                    start_time = datetime.fromisoformat(
                        event["начало"].replace("Z", "+00:00")
                    )

                    duration = event.get("продолжительность", 45)
                    end_time = start_time + timedelta(minutes=duration)
                    delete_time = end_time + timedelta(minutes=15)

                    if now < delete_time:
                        cleaned_events.append(event)

                removed = len(events) - len(cleaned_events)

                if removed:
                    with open(file_path, "w", encoding="utf-8") as file:
                        json.dump(
                            cleaned_events,
                            file,
                            ensure_ascii=False,
                            indent=4,
                        )

                    removed_any = True

                    log.info(
                        f"Removed {removed} expired events from {file_path}"
                    )

            except FileNotFoundError:
                pass

            except Exception as error:
                log.error(
                    f"Failed to clean {file_path}: {error}"
                )

        return removed_any

    def open_add_event_dialog(self):
        dialog = AddEventDialog(self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        event = dialog.get_event()

        event_start = datetime.fromisoformat(
            event["начало"].replace("Z", "+00:00")
        )

        if event_start < datetime.now(timezone.utc):
            message_box = QMessageBox(self)
            message_box.setIcon(QMessageBox.Warning)
            message_box.setWindowTitle("Событие в прошлом")
            message_box.setText("Нельзя создать событие в прошлом.")
            set_dark_title_bar(message_box)
            message_box.exec()
            return

        conflict = self.has_event_conflict(event)

        if conflict:
            log.warning(
                f"Manual event conflicts with existing event: "
                f"{conflict.get('предмет', 'Без названия')}"
            )

            message_box = QMessageBox(self)
            message_box.setIcon(QMessageBox.Warning)
            message_box.setWindowTitle("Пересечение событий")
            message_box.setText(
                "Создаваемое событие пересекается с уже существующим."
            )

            set_dark_title_bar(message_box)

            message_box.exec()
            return
        
        event["id"] = f"manual_{uuid4().hex}"

        try:
            with open(MANUAL_EVENTS_FILE, "r", encoding="utf-8") as file:
                events = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            events = []

        events.append(event)

        with open(MANUAL_EVENTS_FILE, "w", encoding="utf-8") as file:
            json.dump(events, file, ensure_ascii=False, indent=4)

        log.info("Manual event added successfully")

        self.reload_schedule()

    def load_manual_events(self):
        try:
            with open(MANUAL_EVENTS_FILE,"r",encoding="utf-8",) as file:
                return json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):
            return []

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
        self.clean_expired_events()

        try:
            with open(SCHEDULE_FILE,"r",encoding="utf-8",) as file:
                schedule = json.load(file)

        except Exception as error:
            log.error(
                f"Failed to load schedule: {error}"
            )

            error_label = QLabel(
                f"Не удалось загрузить расписание:\n{error}"
            )
            self.content_layout.addWidget(error_label)
            return

        log.info(
            f"Loaded {len(schedule)} schedule events"
        )

        # Добавляем события, созданные вручную
        manual_events = self.load_manual_events()

        schedule.extend(manual_events)

        if manual_events:
            log.info(
                f"Loaded {len(manual_events)} manual events"
            )

        today = datetime.now().astimezone().date()

        schedule = [
            lesson
            for lesson in schedule
            if datetime.fromisoformat(
                lesson["начало"].replace("Z", "+00:00")
            ).astimezone().date() >= today
        ]

        # Сортируем занятия по времени начала
        schedule.sort(
            key=lambda lesson: datetime.fromisoformat(
                lesson["начало"].replace("Z", "+00:00")
            ).astimezone(timezone.utc)
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

        current_card = None
        next_card = None
        closest_difference = None

        # Сначала ищем текущий урок
        for card in self.cards:
            if card.start_time <= now:
                elapsed_seconds = (
                    now - card.start_time
                ).total_seconds()

                if elapsed_seconds < card.duration_minutes * 60:
                    if (
                        current_card is None
                        or card.start_time > current_card.start_time
                    ):
                        current_card = card

        # Если сейчас идёт урок — показываем его
        if current_card is not None:
            lesson = current_card.lesson_data
            subject = current_card.subject

            start_time = (
                current_card.start_time
                .astimezone()
                .strftime("%H:%M")
            )

            link = lesson.get("ссылка")

            if link:
                text = (
                    f'<span style="color:#aaaaaa;">'
                    f"Текущий урок: "
                    f"</span>"
                    f'<a href="{link}" '
                    f'style="color:#e6c65c; '
                    f'text-decoration:underline;">'
                    f"{subject} ({start_time})"
                    f"</a>"
                )
            else:
                text = (
                    f'<span style="color:#aaaaaa;">'
                    f"Текущий урок: "
                    f"</span>"
                    f'<span style="color:#e6c65c;">'
                    f"{subject} ({start_time})"
                    f"</span>"
                )

            self.next_lesson_label.setText(text)
            return

        # Если текущего урока нет — ищем следующий в ближайшие 15 минут
        for card in self.cards:
            difference = (
                card.start_time - now
            ).total_seconds()

            if 0 < difference <= 15 * 60:
                if (
                    closest_difference is None
                    or difference < closest_difference
                ):
                    next_card = card
                    closest_difference = difference

        if next_card is None:
            self.next_lesson_label.setText(
                "В ближайшие 15 минут занятий нет"
            )
            return

        lesson = next_card.lesson_data
        subject = next_card.subject

        start_time = (
            next_card.start_time
            .astimezone()
            .strftime("%H:%M")
        )

        link = lesson.get("ссылка")

        if link:
            text = (
                f'<span style="color:#aaaaaa;">'
                f"Следующий урок: "
                f"</span>"
                f'<a href="{link}" '
                f'style="color:#e6c65c; '
                f'text-decoration:underline;">'
                f"{subject} ({start_time})"
                f"</a>"
            )
        else:
            text = (
                f'<span style="color:#aaaaaa;">'
                f"Следующий урок: "
                f"</span>"
                f'<span style="color:#e6c65c;">'
                f"{subject} ({start_time})"
                f"</span>"
            )

        self.next_lesson_label.setText(text)

    def get_next_lesson(self):
        now = datetime.now(timezone.utc)

        for card in self.cards:
            if card.start_time > now:
                return card

        return None

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
        if self.clean_expired_events():
            self.reload_schedule()

        for card in self.cards:
            card.update_remaining()
            card.setVisible(True)

        self.update_highlight()
        self.update_next_lesson()

        current_lesson = self.get_current_lesson()

        if current_lesson:
            now = datetime.now(timezone.utc)

            seconds_until = (
                current_lesson.start_time - now
            ).total_seconds()

            self.notifications.update(
                current_lesson,
                seconds_until,
            )

            lesson = current_lesson.lesson_data
            lesson_id = lesson.get("id")

            if lesson_id not in self.started_lessons:
                self.started_lessons.add(lesson_id)

                open_ktalk(lesson)
        else:
            next_lesson = self.get_next_lesson()

            if next_lesson:
                now = datetime.now(timezone.utc)

                seconds_until = (
                    next_lesson.start_time - now
                ).total_seconds()

                self.notifications.update(
                    next_lesson,
                    seconds_until,
                )