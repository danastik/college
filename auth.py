import ctypes
from ctypes import wintypes
import json
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)

from logger import logger as log


AUTH_FILE = "./data/auth.json"


class AuthDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Авторизация")
        self.setFixedSize(450, 220)
        self.set_dark_title_bar()

        self.setWindowFlags(
            Qt.Dialog
            | Qt.WindowTitleHint
            | Qt.WindowCloseButtonHint
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            25,
            20,
            25,
            20,
        )

        layout.setSpacing(10)

        title = QLabel("Введите данные аккаунта колледжа")

        email_input = QLineEdit()
        email_input.setPlaceholderText("Email")
        email_input.setFixedHeight(42)

        password_input = QLineEdit()
        password_input.setPlaceholderText("Пароль")
        password_input.setEchoMode(
            QLineEdit.Password    
        )
        password_input.setFixedHeight(42)

        save_button = QPushButton("Сохранить")

        save_button.clicked.connect(
            lambda: self.save_auth(
                email_input.text(),
                password_input.text(),
            )
        )

        self.setStyleSheet(
            """
            QLineEdit {
                background-color: #252525;
                color: #e6e6e6;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 8px 10px;
                min-height: 32px;
            }

            QLineEdit:focus {
                border: 1px solid #f1c75b;
            }

            QPushButton {
                background-color: #f1c75b;
                color: #1e1e1e;
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #f5d477;
            }

            QPushButton:pressed {
                background-color: #dcb44e;
            }

            QLabel {
                background: transparent;
                color: #e6e6e6;
            }
            """
        )

        layout.addWidget(title)
        layout.addWidget(email_input)
        layout.addWidget(password_input)
        layout.addStretch()
        layout.addWidget(save_button)

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

    def save_auth(self, email, password):
        if not email or not password:
            return

        os.makedirs(
            "./data",
            exist_ok=True,
        )

        auth_data = {
            "email": email,
            "password": password,
            "token": "",
        }

        try:
            with open(
                AUTH_FILE,
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    auth_data,
                    file,
                    ensure_ascii=False,
                    indent=4,
                )

            log.info(
                "Authentication data saved"
            )

            self.accept()

        except Exception as error:
            log.error(
                f"Failed to save authentication data: {error}"
            )