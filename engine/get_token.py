import json
import os
import shutil
import subprocess
import winreg

from playwright.sync_api import sync_playwright, TimeoutError

from logger import logger as log

TARGET_URL = "https://app.rameevcollege.ru/study/schedule"
AUTH_FILE = "./data/auth.json"

def find_chrome():
    paths = [
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\Google\Chrome SxS\Application\chrome.exe"),
    ]

    # Проверяем PATH
    chrome = shutil.which("chrome.exe")
    if chrome:
        paths.insert(0, chrome)

    # Проверяем через where.exe
    try:
        result = subprocess.run(
            ["where", "chrome"],
            capture_output=True,
            text=True,
            timeout=3,
        )

        for path in result.stdout.splitlines():
            path = path.strip()
            if os.path.isfile(path):
                paths.insert(0, path)
    except Exception:
        pass

    # Проверяем реестр Windows
    registry_keys = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"),
    ]

    for root, key in registry_keys:
        try:
            with winreg.OpenKey(root, key) as registry:
                path, _ = winreg.QueryValueEx(registry, None)

                if os.path.isfile(path):
                    paths.insert(0, path)
        except (FileNotFoundError, OSError):
            pass

    # Проверяем все найденные варианты
    for path in paths:
        if path and os.path.isfile(path):
            log.info(f"Chrome found: {path}")
            return path

    return None

def get_token():
    log.info("Starting authentication process")

    try:
        with open(AUTH_FILE,"r",encoding="utf-8",) as file:
            auth = json.load(file)

        email = auth["email"]
        password = auth["password"]

    except Exception as error:
        log.error(
            f"Failed to load authentication credentials: {error}"
        )
        raise

    with sync_playwright() as p:
        chrome_path = find_chrome()

        if chrome_path:
            log.info("Using installed Google Chrome")
            browser = p.chromium.launch(
                headless=True,
                executable_path=chrome_path,
            )
        else:
            log.warning("Google Chrome was not found, using Playwright Chromium")
            browser = p.chromium.launch(headless=True)

            page = browser.new_page()

            try:
                log.info(
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

                log.info(
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

                with open(AUTH_FILE,"w",encoding="utf-8",) as file:
                    json.dump(auth,file,ensure_ascii=False,indent=4,)

                log.info(
                    "Authentication token saved successfully"
                )

                return token

            except TimeoutError:
                log.warning(
                    "Authentication page did not load in time; restarting browser"
                )

            except Exception as error:
                log.error(
                    f"Authentication failed: {error}"
                )

            finally:
                browser.close()

                log.info(
                    "Authentication browser closed"
                )