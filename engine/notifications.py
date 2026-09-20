from windows_toasts import Toast, WindowsToaster

class NotificationManager:
    def __init__(self, settings):
        self.settings = settings

        # Уже отправленные уведомления.
        # Формат: (идентификатор занятия, сколько минут заранее)
        self.sent_notifications = set()

        self.toaster = WindowsToaster("Колледж")

    def update(self, lesson_card, seconds_until):
        """
        Проверяет, нужно ли отправить уведомление
        о следующем занятии.

        lesson_card — LessonCard следующего занятия
        seconds_until — точное количество секунд до начала
        """

        if not self.settings.get("notifications", {}).get(
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

        if not self.settings.get(
            "notifications",
            {},
        ).get(notification_type, False):
            return

        notify_in_advance = self.settings.get(
            "notify_in_advance",
            [],
        )

        for minutes in notify_in_advance:
            self.check_notification(
                lesson,
                notification_type,
                seconds_until,
                minutes,
            )

    @staticmethod
    def get_notification_type(lesson):
        if lesson.get("тип") in ("EVENT", "MANUAL_EVENT"):
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
        seconds_until,
        minutes,
    ):
        """
        Проверяет, наступило ли время отправить
        уведомление за указанное количество минут.
        """

        target_seconds = minutes * 60

        if seconds_until <= target_seconds and seconds_until > 0:
            lesson_id = self.get_lesson_id(lesson)

            notification_id = (
                lesson_id,
                minutes,
            )

            if notification_id in self.sent_notifications:
                return

            self.sent_notifications.add(notification_id)

            self._send_notification(
                lesson,
                notification_type,
                minutes,
            )

    @staticmethod
    def get_lesson_id(lesson):
        """
        Получает идентификатор занятия.

        Если в данных есть id — используем его.
        Иначе собираем идентификатор из даты и предмета.
        """

        if lesson.get("id") is not None:
            return str(lesson["id"])

        return (
            str(lesson.get("начало", ""))
            + "_"
            + str(lesson.get("предмет", ""))
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

        toast = Toast()
        toast.text_fields = [
            subject,
            f"Начнётся через {minutes} минут!",
        ]

        self.toaster.show_toast(toast)