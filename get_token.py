import json

from playwright.sync_api import sync_playwright, TimeoutError


TARGET_URL = "https://app.rameevcollege.ru/study/schedule"


# Загружаем данные авторизации
with open("auth.json", "r", encoding="utf-8") as file:
    auth = json.load(file)

EMAIL = auth["email"]
PASSWORD = auth["password"]


with sync_playwright() as p:
    while True:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(TARGET_URL)

        # Заполняем форму
        page.get_by_placeholder("Введите ваш email").fill(EMAIL)
        page.get_by_placeholder("Введите ваш пароль").fill(PASSWORD)

        # Нажимаем "Войти"
        page.get_by_role("button", name="Войти").click()

        try:
            # Ждём появления заголовка "Расписание"
            page.get_by_role("heading", name="Расписание").wait_for(
                state="visible",
                timeout=10000
            )

            print("Успешный вход!")
            # Получаем токен из localStorage
            token = page.evaluate(
                "() => localStorage.getItem('auth._token.local')"
            )

            if token:
                # Убираем "Bearer " из начала токена
                token = token.removeprefix("Bearer ")

                # Сохраняем токен в auth.json
                auth["token"] = token

                with open("auth.json", "w", encoding="utf-8") as file:
                    json.dump(auth, file, ensure_ascii=False, indent=4)

                print("Токен сохранён в auth.json")
            else:
                print("Токен не найден!")
            break

        except TimeoutError:
            print("Элемент 'Расписание' не появился.")
            print(f"Текущий URL: {page.url}")
            print("Перезапускаем...")

            browser.close()