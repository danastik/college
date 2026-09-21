from pathlib import Path
import winsound

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QRect,
    Qt,
    QTimer,
)
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from logger import logger as log


class NotificationWindow(QWidget):
    WIDTH = 360
    HEIGHT = 140

    MARGIN = 20
    DISPLAY_TIME = 5000

    def __init__(
        self,
        subject,
        minutes,
        notification_sound,
        start_notification=False,
    ):
        super().__init__()

        self.subject = subject
        self.minutes = minutes
        self.start_notification = start_notification
        self.notification_sound = notification_sound

        self.setFixedSize(
            self.WIDTH,
            self.HEIGHT,
        )

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )

        self.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.build_ui()

        self.animation = None

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        app = QApplication.instance()

        if app is None:
            return

        for window in app.topLevelWidgets():
            if window is self:
                continue

            if window.isWindow() and window.isVisible():
                window.showNormal()
                window.raise_()
                window.activateWindow()
                break

    def build_ui(self):
        container = QFrame(self)

        container.setGeometry(
            0,
            0,
            self.WIDTH,
            self.HEIGHT,
        )

        container.setStyleSheet(
            """
            QFrame {
                background: #252525;
                border: 1px solid #f1c75b;
                border-radius: 12px;
            }

            QLabel {
                background: transparent;
                border: none;
                color: #e6e6e6;
            }

            QPushButton {
                background: transparent;
                border: none;
                color: #888888;
                font-size: 18px;
            }

            QPushButton:hover {
                color: #ffffff;
            }
            """
        )

        layout = QVBoxLayout(container)

        layout.setContentsMargins(
            18,
            12,
            14,
            14,
        )

        layout.setSpacing(0)

        top_layout = QHBoxLayout()

        top_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        title = QLabel("Колледж")

        title.setFont(
            QFont(
                "Segoe UI",
                10,
                QFont.Weight.Bold,
            )
        )

        title.setStyleSheet(
            "color: #f1c75b;"
        )

        close_button = QPushButton("×")

        close_button.setFixedSize(
            24,
            24,
        )

        close_button.clicked.connect(
            self.close_with_animation
        )

        top_layout.addWidget(title)
        top_layout.addStretch()
        top_layout.addWidget(close_button)

        layout.addLayout(top_layout)
        layout.addSpacing(5)

        subject_label = QLabel(
            self.subject
        )

        subject_label.setContentsMargins(
            0,
            15,
            0,
            0,
        )

        subject_label.setFont(
            QFont(
                "Segoe UI",
                15,
                QFont.Weight.Bold,
            )
        )

        subject_label.setStyleSheet(
            "color: #f0f0f0;"
        )

        layout.addWidget(
            subject_label
        )
        layout.addSpacing(0)

        if self.start_notification:
            text = QLabel(
                "начинается!"
            )
        else:
            text = QLabel(
                f"Начнётся через {self.minutes} минут"
            )

        text.setFont(
            QFont(
                "Segoe UI",
                14,
                QFont.Weight.Normal,
            )
        )

        text.setStyleSheet(
            "color: #d0d0d0;"
        )

        layout.addWidget(text)

    def showEvent(self, event):
        super().showEvent(event)

        self.position_window()
        self.play_sound()
        self.animate_in()

        QTimer.singleShot(
            self.DISPLAY_TIME,
            self.close_with_animation,
        )

    def position_window(self):
        screen = QApplication.primaryScreen()

        if screen is None:
            return

        geometry = screen.availableGeometry()

        target_x = (
            geometry.right()
            - self.WIDTH
            - self.MARGIN
        )

        target_y = (
            geometry.bottom()
            - self.HEIGHT
            - self.MARGIN
        )

        self.target_geometry = QRect(
            target_x,
            target_y,
            self.WIDTH,
            self.HEIGHT,
        )

        start_geometry = QRect(
            geometry.right() + 1,
            target_y,
            self.WIDTH,
            self.HEIGHT,
        )

        self.setGeometry(
            start_geometry
        )

    def animate_in(self):
        self.animation = QPropertyAnimation(
            self,
            b"geometry",
        )

        self.animation.setDuration(300)

        self.animation.setStartValue(
            self.geometry()
        )

        self.animation.setEndValue(
            self.target_geometry
        )

        self.animation.setEasingCurve(
            QEasingCurve.OutCubic
        )

        self.animation.start()

    def close_with_animation(self):
        if self.animation is not None:
            self.animation.stop()

        animation = QPropertyAnimation(
            self,
            b"geometry",
        )

        animation.setDuration(250)

        animation.setStartValue(
            self.geometry()
        )

        end_geometry = QRect(
            self.geometry().right() + 1,
            self.geometry().y(),
            self.WIDTH,
            self.HEIGHT,
        )

        animation.setEndValue(
            end_geometry
        )

        animation.setEasingCurve(
            QEasingCurve.InCubic
        )

        animation.finished.connect(
            self.close
        )

        animation.start()

        self.animation = animation

    def play_sound(self):
        sound_path = (
            Path("./assets")
            / self.notification_sound
        ).resolve()

        if not sound_path.exists():
            log.warning(
                f"Notification sound file not found: {sound_path.name}"
            )
            return

        try:
            log.info(
                f"Playing notification sound: {sound_path.name}"
            )

            winsound.PlaySound(
                str(sound_path),
                winsound.SND_FILENAME
                | winsound.SND_ASYNC,
            )

        except Exception as error:
            log.error(
                f"Failed to play notification sound: {error}"
            )