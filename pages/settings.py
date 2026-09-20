import json

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QLineEdit,
    QComboBox,
    QPushButton,
    QFrame,
)

from logger import logger


SETTINGS_FILE = "./data/settings.json"


class SettingsPage(QWidget):
    def __init__(self, settings):
        super().__init__()

        self.settings = settings

        self.build_ui()
        self.load_settings()

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

                # =========================================================
        # Верхняя часть: Уведомления + kTalk
        # =========================================================

        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)

        # =========================================================
        # Уведомления
        # =========================================================

        notifications_frame = QFrame()
        notifications_frame.setObjectName("settingsFrame")

        notifications_layout = QVBoxLayout(
            notifications_frame
        )
        notifications_layout.setContentsMargins(
            15,
            15,
            15,
            15,
        )
        notifications_layout.setSpacing(12)

        notifications_title = QLabel(
            "Уведомления"
        )
        notifications_title.setObjectName(
            "settingsTitle"
        )

        self.notifications_enabled = QCheckBox(
            "Уведомления"
        )

        self.practice_notifications = QCheckBox(
            "Уведомлять о практике"
        )

        notifications_layout.addWidget(
            notifications_title
        )
        notifications_layout.addWidget(
            self.notifications_enabled
        )
        notifications_layout.addWidget(
            self.practice_notifications
        )
        notifications_layout.addStretch()

        # =========================================================
        # kTalk
        # =========================================================

        ktalk_frame = QFrame()
        ktalk_frame.setObjectName(
            "settingsFrame"
        )

        ktalk_layout = QVBoxLayout(
            ktalk_frame
        )
        ktalk_layout.setContentsMargins(
            15,
            15,
            15,
            15,
        )
        ktalk_layout.setSpacing(12)

        ktalk_title = QLabel(
            "kTalk"
        )
        ktalk_title.setObjectName(
            "settingsTitle"
        )

        self.auto_open_ktalk = QCheckBox(
            "Автоматически открывать kTalk"
        )

        ktalk_layout.addWidget(
            ktalk_title
        )
        ktalk_layout.addWidget(
            self.auto_open_ktalk
        )
        ktalk_layout.addStretch()

        top_layout.addWidget(
            notifications_frame
        )
        top_layout.addWidget(
            ktalk_frame
        )

        # =========================================================
        # Дополнительные настройки уведомлений
        # =========================================================

        notification_options_frame = QFrame()
        notification_options_frame.setObjectName(
            "settingsFrame"
        )

        notification_options_layout = QHBoxLayout(
            notification_options_frame
        )
        notification_options_layout.setContentsMargins(
            15,
            15,
            15,
            15,
        )
        notification_options_layout.setSpacing(15)

        # Уведомлять заранее

        advance_label = QLabel(
            "Уведомлять за:"
        )

        self.notify_in_advance = QLineEdit()
        self.notify_in_advance.setPlaceholderText(
            "Например: 10, 5"
        )
        self.notify_in_advance.setFixedWidth(120)

        minutes_label = QLabel(
            "мин."
        )

        notification_options_layout.addWidget(
            advance_label
        )
        notification_options_layout.addWidget(
            self.notify_in_advance
        )
        notification_options_layout.addWidget(
            minutes_label
        )

        notification_options_layout.addSpacing(20)

        # Звук уведомления

        sound_label = QLabel(
            "Звук уведомления:"
        )

        self.notification_sound = QComboBox()

        self.notification_sound.addItems([
            "notification1.wav",
            "notification2.wav",
            "notification3.wav",
            "notification4.wav",
            "notification5.wav",
        ])

        notification_options_layout.addWidget(
            sound_label
        )
        notification_options_layout.addWidget(
            self.notification_sound
        )
        notification_options_layout.addStretch()

        # =========================================================
        # Расписание
        # =========================================================

        schedule_frame = QFrame()
        schedule_frame.setObjectName(
            "settingsFrame"
        )

        schedule_layout = QVBoxLayout(
            schedule_frame
        )
        schedule_layout.setContentsMargins(
            15,
            15,
            15,
            15,
        )
        schedule_layout.setSpacing(12)

        schedule_title = QLabel(
            "Расписание"
        )
        schedule_title.setObjectName(
            "settingsTitle"
        )

        update_layout = QHBoxLayout()

        update_label = QLabel(
            "Частота обновления:"
        )

        self.update_frequency = QLineEdit()
        self.update_frequency.setPlaceholderText(
            "Например: 60"
        )
        self.update_frequency.setFixedWidth(
            120
        )

        update_seconds_label = QLabel(
            "сек."
        )

        update_layout.addWidget(
            update_label
        )
        update_layout.addWidget(
            self.update_frequency
        )
        update_layout.addWidget(
            update_seconds_label
        )
        update_layout.addStretch()

        schedule_layout.addWidget(
            schedule_title
        )
        schedule_layout.addLayout(
            update_layout
        )
        schedule_layout.addStretch()

        # =========================================================
        # Кнопка сохранения
        # =========================================================

        save_button = QPushButton(
            "Сохранить"
        )

        save_button.setObjectName(
            "saveButton"
        )

        save_button.setFixedHeight(40)

        save_button.clicked.connect(
            self.save_settings
        )

        # =========================================================
        # Добавляем всё на страницу
        # =========================================================

        main_layout.addLayout(
            top_layout
        )

        main_layout.addWidget(
            notification_options_frame
        )

        main_layout.addWidget(
            schedule_frame
        )

        main_layout.addStretch()

        main_layout.addWidget(
            save_button
        )

        # =========================================================
        # Стили
        # =========================================================

        self.setStyleSheet(
            """
            QFrame#settingsFrame {
                background: #252525;
                border: 1px solid #3a3a3a;
                border-radius: 10px;
            }

            QLabel#settingsTitle {
                color: #ffffff;
                font-size: 15px;
                font-weight: bold;
                background: transparent;
            }

            QLabel {
                color: #c8c8c8;
                background: transparent;
            }

            QCheckBox {
                color: #c8c8c8;
                background: transparent;
                spacing: 8px;
            }

            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 4px;
            }

            QCheckBox::indicator:unchecked {
                background: #303030;
                border: 1px solid #555555;
            }

            QCheckBox::indicator:checked {
                background: #e0ba57;
                border: 1px solid #e0ba57;
            }

            QCheckBox::indicator:checked:hover {
                background: #e8c367;
                border: 1px solid #e8c367;
            }

            QLineEdit,
            QComboBox {
                background: #303030;
                color: #e0e0e0;
                border: 1px solid #454545;
                border-radius: 6px;
                padding: 6px 8px;
            }

            QLineEdit:focus,
            QComboBox:focus {
                border: 1px solid #d5ad4c;
            }

            QComboBox {
                padding-right: 28px;
            }

            QComboBox::drop-down {
                width: 24px;
                border: none;
                background: transparent;
            }

            QComboBox QAbstractItemView {
                background: #303030;
                color: #e0e0e0;
                border: 1px solid #454545;
                selection-background-color: #3d3d3d;
                selection-color: #ffffff;
            }

            QPushButton#saveButton {
                background: #d5ad4c;
                color: #202020;
                border: none;
                border-radius: 7px;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton#saveButton:hover {
                background: #e0ba57;
            }

            QPushButton#saveButton:pressed {
                background: #bd963d;
            }
            """
        )

    def load_settings(self):
        notifications = self.settings.get(
            "notifications",
            {},
        )

        # Уведомления
        self.notifications_enabled.setChecked(
            notifications.get(
                "enabled",
                True,
            )
        )

        # Практика
        self.practice_notifications.setChecked(
            notifications.get(
                "practice",
                True,
            )
        )

        # Уведомлять заранее
        notify_in_advance = self.settings.get(
            "notify_in_advance",
            [10, 5],
        )

        if isinstance(
            notify_in_advance,
            list,
        ):
            self.notify_in_advance.setText(
                ", ".join(
                    str(value)
                    for value in notify_in_advance
                )
            )
        else:
            self.notify_in_advance.setText(
                str(notify_in_advance)
            )

        # Звук
        notification_sound = self.settings.get(
            "notification_sound",
            "notification1.wav",
        )

        index = self.notification_sound.findText(
            notification_sound
        )

        if index >= 0:
            self.notification_sound.setCurrentIndex(
                index
            )

        # Расписание
        update_frequency = self.settings.get(
            "update_frequency",
            "60",
        )

        self.update_frequency.setText(
            str(update_frequency)
        )

        # kTalk
        self.auto_open_ktalk.setChecked(
            self.settings.get(
                "auto_open_ktalk",
                True,
            )
        )

        # self.auto_join_ktalk.setChecked(
        #     self.settings.get(
        #         "auto_join_ktalk",
        #         True,
        #     )
        # )

        logger.info(
            "Application settings loaded into settings page"
        )

    def save_settings(self):
        # =========================================================
        # Уведомления
        # =========================================================

        notifications = self.settings.setdefault(
            "notifications",
            {},
        )

        notifications["enabled"] = (
            self.notifications_enabled.isChecked()
        )

        notifications["practice"] = (
            self.practice_notifications.isChecked()
        )

        # =========================================================
        # Уведомлять заранее
        # =========================================================

        text = self.notify_in_advance.text()

        values = []

        for value in text.replace(
            ";",
            ",",
        ).split(","):
            value = value.strip()

            if not value:
                continue

            try:
                number = int(value)

                if number >= 0:
                    values.append(number)

            except ValueError:
                continue

        self.settings["notify_in_advance"] = values

        # =========================================================
        # Звук
        # =========================================================

        self.settings["notification_sound"] = (
            self.notification_sound.currentText()
        )

        # =========================================================
        # Расписание
        # =========================================================

        self.settings["update_frequency"] = (
            self.update_frequency.text()
        )

        # =========================================================
        # kTalk
        # =========================================================

        self.settings["auto_open_ktalk"] = (
            self.auto_open_ktalk.isChecked()
        )

        # self.settings["auto_join_ktalk"] = (
        #     self.auto_join_ktalk.isChecked()
        # )

        # =========================================================
        # Сохранение settings.json
        # =========================================================

        try:
            with open(
                SETTINGS_FILE,
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    self.settings,
                    file,
                    ensure_ascii=False,
                    indent=4,
                )

            logger.info(
                "Application settings saved successfully"
            )

        except Exception as error:
            logger.error(
                f"Failed to save application settings: {error}"
            )