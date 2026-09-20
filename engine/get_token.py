import json

from playwright.sync_api import sync_playwright, TimeoutError

from logger import logger


TARGET_URL = "https://app.rameevcollege.ru/study/schedule"
AUTH_FILE = "./data/auth.json"


def get_token():
    logger.info("Starting authentication process")

    try:
        with open(
            AUTH_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            auth = json.load(file)

        email = auth["email"]
        password = auth["password"]

    except Exception as error:
        logger.error(
            f"Failed to load authentication credentials: {error}"
        )
        raise

    with sync_playwright() as p:
        while True:
            browser = p.chromium.launch(
                headless=True
            )

            page = browser.new_page()

            try:
                logger.info(
                    "Opening authentication page"
                )

                page.goto(TARGET_URL)

                page.get_by_placeholder(
                    "Введите ваш email"
                ).fill(email)

                page.get_by_placeholder(
                    "Введите ваш пароль"
                ).fill(password)

                page.get_by_role(
                    "button",
                    name="Войти",
                ).click()

                page.get_by_role(
                    "heading",
                    name="Расписание",
                ).wait_for(
                    state="visible",
                    timeout=10000,
                )

                logger.info(
                    "Authentication completed successfully"
                )

                token = page.evaluate(
                    "() => localStorage.getItem('auth._token.local')"
                )

                if not token:
                    raise RuntimeError(
                        "Authentication token was not found"
                    )

                token = token.removeprefix(
                    "Bearer "
                )

                auth["token"] = token

                with open(
                    AUTH_FILE,
                    "w",
                    encoding="utf-8",
                ) as file:
                    json.dump(
                        auth,
                        file,
                        ensure_ascii=False,
                        indent=4,
                    )

                logger.info(
                    "Authentication token saved successfully"
                )

                return token

            except TimeoutError:
                logger.warning(
                    "Authentication page did not load in time; restarting browser"
                )

            except Exception as error:
                logger.error(
                    f"Authentication failed: {error}"
                )

            finally:
                browser.close()

                logger.info(
                    "Authentication browser closed"
                )