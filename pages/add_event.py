import ctypes
from ctypes import wintypes
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QPushButton,
)


class AddEventDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Добавить событие")
        self.setFixedSize(420, 500)

        # Тёмная системная шапка окна
        self.set_dark_title_bar()

        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }

            QLabel {
                color: #aaaaaa;
                font-size: 13px;
            }

            QLabel#title {
                color: #e6e6e6;
                font-size: 22px;
                font-weight: bold;
            }

            QLabel#description {
                color: #777777;
                font-size: 13px;
            }

            QLineEdit,
            QSpinBox {
                background-color: #252525;
                color: #e6e6e6;

                border: 1px solid #333333;
                border-radius: 7px;

                padding: 9px 10px;

                font-size: 14px;
            }

            QLineEdit:focus,
            QSpinBox:focus {
                border: 1px solid #555555;
            }

            QPushButton {
                background-color: #303030;
                color: #aaaaaa;

                border: none;
                border-radius: 7px;

                padding: 10px 20px;

                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #3a3a3a;
                color: white;
            }

            QPushButton:pressed {
                background-color: #454545;
            }

            QPushButton#addButton {
                background-color: #f1c75b;
                color: #1e1e1e;
                font-weight: bold;
            }

            QPushButton#addButton:hover {
                background-color: #f6d477;
            }

            QPushButton#addButton:pressed {
                background-color: #d9b34f;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 22, 25, 22)
        main_layout.setSpacing(14)

        # Заголовок
        title = QLabel("Добавить событие")
        title.setObjectName("title")

        description = QLabel(
            "Добавьте занятие, о котором вам сообщили лично."
        )
        description.setObjectName("description")

        main_layout.addWidget(title)
        main_layout.addWidget(description)

        main_layout.addSpacing(8)

        # Название
        subject_label = QLabel("Название")

        self.subject_edit = QLineEdit()
        self.subject_edit.setPlaceholderText(
            "Например: Встреча с Куратором"
        )

        main_layout.addWidget(subject_label)
        main_layout.addWidget(self.subject_edit)

        # Дата и время
        date_time_layout = QHBoxLayout()
        date_time_layout.setSpacing(10)

        # Дата
        date_layout = QVBoxLayout()
        date_layout.setSpacing(5)

        date_label = QLabel("Дата")

        self.date_edit = QLineEdit()
        self.date_edit.setPlaceholderText(datetime.now().strftime("%d.%m.%Y"))

        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)

        # Время
        time_layout = QVBoxLayout()
        time_layout.setSpacing(5)

        time_label = QLabel("Время")

        self.time_edit = QLineEdit()
        self.time_edit.setPlaceholderText("14:30")

        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_edit)

        date_time_layout.addLayout(date_layout)
        date_time_layout.addLayout(time_layout)

        main_layout.addLayout(date_time_layout)

        # Длительность
        duration_label = QLabel("Длительность")

        self.duration_edit = QSpinBox()
        self.duration_edit.setRange(1, 1440)
        self.duration_edit.setValue(45)
        self.duration_edit.setSuffix(" мин.")

        main_layout.addWidget(duration_label)
        main_layout.addWidget(self.duration_edit)

        # Ссылка
        link_label = QLabel()
        link_label.setText(
            "Ссылка "
            "<span style='color:#666666'>(необязательно)</span>"
        )

        self.link_edit = QLineEdit()
        self.link_edit.setPlaceholderText("https://...")

        main_layout.addWidget(link_label)
        main_layout.addWidget(self.link_edit)

        main_layout.addStretch()

        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        cancel_button = QPushButton("Отмена")
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.clicked.connect(self.reject)

        add_button = QPushButton("Добавить")
        add_button.setObjectName("addButton")
        add_button.setCursor(Qt.PointingHandCursor)
        add_button.clicked.connect(self.accept)

        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(add_button)

        main_layout.addLayout(buttons_layout)

        self.subject_edit.setFocus()

    def set_dark_title_bar(self):
        hwnd = int(self.winId())

        DWMWA_USE_IMMERSIVE_DARK_MODE = 20

        value = ctypes.c_int(1)

        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            wintypes.HWND(hwnd),
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(value),
            ctypes.sizeof(value),
        )

    def get_event(self):
        date_text = self.date_edit.text().strip()
        time_text = self.time_edit.text().strip()

        start_time = datetime.strptime(
            f"{date_text} {time_text}",
            "%d.%m.%Y %H:%M",
        ).astimezone()

        return {
            "начало": start_time.isoformat(
                timespec="milliseconds"
            ),
            "тип": "MANUAL_EVENT",
            "продолжительность": self.duration_edit.value(),
            "предмет": self.subject_edit.text().strip(),
            "занятия": [],
            "преподаватель": None,
            "описание": "Личное событие",
            "ссылка": self.link_edit.text().strip() or None,
        }