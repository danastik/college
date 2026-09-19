from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QSizePolicy,
)

from pages.schedule import SchedulePage
from pages.settings import SettingsPage
from pages.logs import LogsPage


class AppWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Расписание")
        self.resize(700, 500)

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

        self.schedule_page = SchedulePage()
        self.settings_page = SettingsPage()
        self.logs_page = LogsPage()

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

    def change_page(self, index):
        self.stack.setCurrentIndex(index)

        for i, button in enumerate(self.buttons):
            button.setProperty("active", i == index)

            button.style().unpolish(button)
            button.style().polish(button)


def run_app():
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
    """)

    window = AppWindow()
    window.show()

    app.exec()


if __name__ == "__main__":
    run_app()