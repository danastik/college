import os
import ctypes
from ctypes import wintypes

from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QSizePolicy,
    QDialog,
)

from auth import AuthDialog
from pages.schedule import SchedulePage
from pages.settings import SettingsPage
from pages.logs import LogsPage
from logger import logger


class ScheduleUpdateNotifier(QObject):
    updated = Signal()


class AppWindow(QWidget):
    def __init__(self, notifier=None, settings=None):
        super().__init__()

        self.setWindowTitle("College Helper")
        self.resize(700, 500)

        self.set_dark_title_bar()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        tabs_layout = QHBoxLayout()
        tabs_layout.setSpacing(5)

        self.schedule_button = QPushButton("📅  Расписание")
        self.settings_button = QPushButton("⚙  Настройки")
        self.logs_button = QPushButton("📄  Логи")

        self.buttons = [
            self.schedule_button,
            self.settings_button,
            self.logs_button,
        ]

        for button in self.buttons:
            button.setCursor(Qt.PointingHandCursor)
            button.setMinimumHeight(50)
            button.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Fixed,
            )

            tabs_layout.addWidget(button)

        self.stack = QStackedWidget()

        self.schedule_page = SchedulePage(settings)
        self.settings_page = SettingsPage(settings)
        self.logs_page = LogsPage()

        if notifier is not None:
            notifier.updated.connect(
                self.schedule_page.reload_schedule
            )

        self.stack.addWidget(self.schedule_page)
        self.stack.addWidget(self.settings_page)
        self.stack.addWidget(self.logs_page)

        self.schedule_button.clicked.connect(
            lambda: self.change_page(0)
        )
        self.settings_button.clicked.connect(
            lambda: self.change_page(1)
        )
        self.logs_button.clicked.connect(
            lambda: self.change_page(2)
        )

        main_layout.addLayout(tabs_layout)
        main_layout.addWidget(self.stack)

        self.change_page(0)

        logger.info("Main window initialized")

    def set_dark_title_bar(self):
        hwnd = int(self.winId())

        DWMWA_USE_IMMERSIVE_DARK_MODE = 20

        value = ctypes.c_int(1)

        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            wintypes.HWND(hwnd),
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(value),
            ctypes.sizeof(value)
        )

    def change_page(self, index):
        self.stack.setCurrentIndex(index)

        for i, button in enumerate(self.buttons):
            button.setProperty("active", i == index)

            button.style().unpolish(button)
            button.style().polish(button)


def run_app(notifier=None, settings=None):
    logger.info("Initializing application interface")

    app = QApplication([])

    app.setStyleSheet("""
        QWidget {
            background-color: #1e1e1e;
            color: #e6e6e6;
        }

        QPushButton {
            background-color: #252525;
            color: #aaaaaa;

            border: none;
            border-radius: 8px;

            padding: 10px 20px;

            font-size: 14px;
        }

        QPushButton:hover {
            background-color: #303030;
            color: white;
        }

        QPushButton:pressed {
            background-color: #353535;
        }

        QPushButton[active="true"] {
            background-color: #3a3a3a;
            color: white;
        }

        QStackedWidget {
            background-color: #181818;
            border-radius: 8px;
        }


        /* Карточка занятия */

        QFrame#lessonCard {
            background-color: #252525;
            border-radius: 8px;
            border: 1px solid transparent;
        }

        QFrame#lessonCard[highlighted="true"] {
            border: 1px solid #f1c75b;
        }


        /* Тип занятия: урок */

        QFrame#lesson {
            background-color: #5dade2;
            border-radius: 3px;
        }


        /* Тип занятия: практическая */

        QFrame#practice {
            background-color: #58b368;
            border-radius: 3px;
        }


        /* Тип занятия: особая встреча */

        QFrame#special {
            background-color: #f1c75b;
            border-radius: 3px;
        }


        /* Нижняя информационная панель */

        QFrame#scheduleInfo {
            background-color: #252525;
            border-radius: 8px;
        }


        /* Тексты в карточке занятия */

        QLabel#lessonTime,
        QLabel#lessonSubject,
        QLabel#lessonRemaining {
            background-color: #252525;
            border-radius: 6px;
            padding: 4px 8px;
        }


        /* Заголовок дня */

        QLabel#dayHeader {
            background-color: #252525;
            border-radius: 6px;
            padding: 5px 10px;
        }


        /* Следующий урок и легенда */

        QLabel#nextLesson,
        QLabel#lessonLegend,
        QLabel#practiceLegend,
        QLabel#specialLegend {
            background-color: #252525;
            border-radius: 6px;
            padding: 3px 4px;
        }

        QLabel#nextLesson {
            color: #aaaaaa;
        }

        QLabel#nextLesson a {
            color: #e6c65c;
            text-decoration: none;
        }

        QLabel#nextLesson a:hover {
            color: #f0d878;
        }


        /* Кнопка + */

        QPushButton#addButton {
            background-color: #303030;
            color: #aaaaaa;

            border: none;
            border-radius: 8px;

            font-size: 22px;
            font-weight: bold;

            padding: 0px;
            margin: 0px;
        }

        QPushButton#addButton:hover {
            background-color: #3a3a3a;
            color: white;
        }
    """)

    auth_file = "./data/auth.json"

    if not os.path.exists(auth_file):
        dialog = AuthDialog()

        if dialog.exec() != QDialog.Accepted:
            logger.info(
                "Authentication setup cancelled"
            )
            return

    window = AppWindow(notifier, settings)
    window.show()

    logger.info("Application interface started")

    app.exec()

    logger.info("Application closed")


if __name__ == "__main__":
    run_app()