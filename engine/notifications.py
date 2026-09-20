import os
import json
from PySide6.QtCore import QObject

from engine.notification_window import (
    NotificationWindow,
)


class NotificationManager:
    def __init__(self, settings):
        self.settings = settings
        self.sent_notifications = set()
        self.windows = []

        self.settings_mtime = None
        self.settings = settings
        self.sent_notifications = set()

        self.windows = []

    def update(self, lesson_card, seconds_until):
        self.load_settings_if_changed()
        notifications = self.settings.get(
            "notifications",
            {},
        )

        if not notifications.get(
            "enabled",
            True,
        ):
            return

        lesson = lesson_card.lesson_data

        notification_type = self.get_notification_type(
            lesson
        )

        if notification_type is None:
            return

        if not notifications.get(
            notification_type,
            False,
        ):
            return

        notify_in_advance = self.settings.get(
            "notify_in_advance",
            [],
        )

        for minutes in notify_in_advance:
            self.check_notification(
                lesson,
                notification_type,
                minutes,
                seconds_until,
            )

    def load_settings_if_changed(self):
        settings_path = "./data/settings.json"

        try:
            mtime = os.path.getmtime(
                settings_path
            )

            if mtime == self.settings_mtime:
                return

            with open(
                settings_path,
                "r",
                encoding="utf-8",
            ) as file:
                self.settings = json.load(file)

            self.settings_mtime = mtime

            print("Настройки обновлены")

        except Exception as error:
            print(
                "Ошибка загрузки settings.json:",
                error,
            )

    def load_settings(self):
        try:
            with open(
                "./data/settings.json",
                "r",
                encoding="utf-8",
            ) as file:
                self.settings = json.load(file)

        except Exception as error:
            print(
                "Ошибка загрузки settings.json:",
                error,
            )

    @staticmethod
    def get_notification_type(lesson):
        lesson_type = lesson.get("тип")

        if lesson_type in (
            "EVENT",
            "MANUAL_EVENT",
        ):
            return "lesson"

        description = lesson.get("описание")

        if description == "Встреча с преподавателем":
            return "lesson"

        if description == "Работа на платформе":
            return "practice"

        return None

    def check_notification(
        self,
        lesson,
        notification_type,
        minutes,
        seconds_until,
    ):
        target_seconds = minutes * 60

        if (
            seconds_until <= target_seconds
            and seconds_until > 0
        ):
            lesson_id = self.get_lesson_id(
                lesson
            )

            notification_id = (
                lesson_id,
                minutes,
            )

            if notification_id in self.sent_notifications:
                return

            self.sent_notifications.add(
                notification_id
            )

            self._send_notification(
                lesson,
                notification_type,
                minutes,
            )

    @staticmethod
    def get_lesson_id(lesson):
        lesson_id = lesson.get("id")

        if lesson_id:
            return lesson_id

        return (
            f"{lesson.get('начало', '')}_"
            f"{lesson.get('предмет', '')}"
        )

    def _send_notification(
        self,
        lesson,
        notification_type,
        minutes,
    ):
        subject = lesson.get(
            "предмет",
            "Занятие",
        )

        window = NotificationWindow(
            subject,
            minutes,
            self.settings.get(
                "notification_sound",
                "notification.wav",
            ),
        )

        self.windows.append(window)

        window.destroyed.connect(
            lambda: self._remove_window(
                window
            )
        )

        window.show()

    def _remove_window(self, window):
        if window in self.windows:
            self.windows.remove(window)