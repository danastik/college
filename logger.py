import logging
import os


LOG_FILE = "./data/logs/app.log"
MAX_LOG_LINES = 100


os.makedirs(
    os.path.dirname(LOG_FILE),
    exist_ok=True,
)


class LimitedFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.trim_log()

    def trim_log(self):
        try:
            with open(
                LOG_FILE,
                "r",
                encoding="utf-8",
            ) as file:
                lines = file.readlines()

            if len(lines) <= MAX_LOG_LINES:
                return

            lines = lines[-MAX_LOG_LINES:]

            with open(
                LOG_FILE,
                "w",
                encoding="utf-8",
            ) as file:
                file.writelines(lines)

        except Exception:
            pass


logger = logging.getLogger("college_helper")
logger.setLevel(logging.INFO)


if not logger.handlers:
    file_handler = LimitedFileHandler(
        LOG_FILE,
        encoding="utf-8",
    )

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)