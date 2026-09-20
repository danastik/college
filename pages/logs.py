import os

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPlainTextEdit,
)


LOG_FILE = "./data/logs/app.log"


class LogsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.logs = QPlainTextEdit()
        self.logs.setReadOnly(True)

        self.logs.setStyleSheet("""
            QPlainTextEdit {
                background-color: #181818;
                color: #d0d0d0;

                border: none;
                border-radius: 8px;

                padding: 10px;

                font-family: Consolas;
                font-size: 12px;
            }

            QScrollBar:vertical {
                background-color: #202020;
                width: 8px;
                border: none;
            }

            QScrollBar::handle:vertical {
                background-color: #454545;
                min-height: 20px;
                border-radius: 2px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #555555;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background-color: #202020;
            }
        """)

        layout.addWidget(self.logs)

        self.last_position = 0

        self.load_logs()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_for_updates)
        self.timer.start(500)

    def load_logs(self):
        if not os.path.exists(LOG_FILE):
            self.logs.clear()
            self.last_position = 0
            return

        try:
            with open(
                LOG_FILE,
                "r",
                encoding="utf-8",
            ) as file:
                content = file.read()

            self.logs.setPlainText(content)

            self.last_position = len(content)

            self.scroll_to_bottom()

        except Exception:
            pass

    def check_for_updates(self):
        if not os.path.exists(LOG_FILE):
            return

        try:
            with open(
                LOG_FILE,
                "r",
                encoding="utf-8",
            ) as file:
                file.seek(self.last_position)
                new_content = file.read()

                if not new_content:
                    return

                self.last_position = file.tell()

            scrollbar = self.logs.verticalScrollBar()
            at_bottom = (
                scrollbar.value()
                >= scrollbar.maximum() - 10
            )

            self.logs.moveCursor(
                self.logs.textCursor().End
            )

            self.logs.insertPlainText(new_content)

            if at_bottom:
                self.scroll_to_bottom()

        except Exception:
            pass

    def scroll_to_bottom(self):
        scrollbar = self.logs.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())