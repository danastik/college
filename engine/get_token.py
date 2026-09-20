import json

from playwright.sync_api import sync_playwright, TimeoutError


TARGET_URL = "https://app.rameevcollege.ru/study/schedule"
AUTH_FILE = "./data/auth.json"


def get_token():
    # Загружаем данные авторизации
    with open(AUTH_FILE, "r", encoding="utf-8") as file:
        auth = json.load(file)

    email = auth["email"]
    password = auth["password"]

    with sync_playwright() as p:
        while True:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                page.goto(TARGET_URL)

                # Заполняем форму
                page.get_by_placeholder("Введите ваш email").fill(email)
                page.get_by_placeholder("Введите ваш пароль").fill(password)

                # Нажимаем "Войти"
                page.get_by_role("button", name="Войти").click()

                # Ждём появления заголовка "Расписание"
                page.get_by_role("heading", name="Расписание").wait_for(
                    state="visible",
                    timeout=10000,
                )

                print("Успешный вход!")

                # Получаем токен из localStorage
                token = page.evaluate(
                    "() => localStorage.getItem('auth._token.local')"
                )

                if not token:
                    raise RuntimeError("Токен не найден в localStorage")

                # Убираем "Bearer " из начала токена
                token = token.removeprefix("Bearer ")

                # Сохраняем новый токен
                auth["token"] = token

                with open(AUTH_FILE, "w", encoding="utf-8") as file:
                    json.dump(
                        auth,
                        file,
                        ensure_ascii=False,
                        indent=4,
                    )

                print("Токен сохранён в auth.json")

                return token

            except TimeoutError:
                print("Элемент 'Расписание' не появился.")
                print(f"Текущий URL: {page.url}")
                print("Перезапускаем браузер...")

            finally:
                browser.close()