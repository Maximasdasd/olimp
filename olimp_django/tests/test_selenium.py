"""
E2E-тесты через Selenium (опционально).

⚠️ ВАЖНО: эти тесты НЕ запускаются вместе с остальными по умолчанию
(в pytest.ini задано addopts = -m "not selenium").

Они требуют:
  * установленного Selenium и webdriver-manager;
  * установленного Chrome/Chromium и chromedriver;
  * запущенного FastAPI-бэкенда на 127.0.0.1:8000 с данными (иначе вход не
    пройдёт — аутентификация идёт через FastAPI);
  * live_server из pytest-django (поднимает Django на время теста).

Запуск только этих тестов:
    pytest tests/test_selenium.py -m selenium

Пропустить их в обычном прогоне (поведение по умолчанию):
    pytest -m "not selenium"
"""
import pytest

selenium = pytest.importorskip("selenium")  # пропустить, если selenium не установлен
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture(scope="module")
def driver():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=options)
    yield drv
    drv.quit()


@pytest.mark.selenium
class TestSeleniumE2E:
    """Базовые E2E-сценарии. Требуют live_server + запущенный FastAPI."""

    def test_olympiad_list_page_loads(self, driver, live_server):
        driver.get(f"{live_server.url}/")
        assert "Олимпиад" in driver.page_source

    def test_login_page_has_form(self, driver, live_server):
        driver.get(f"{live_server.url}/login/")
        username = driver.find_element(By.NAME, "username")
        password = driver.find_element(By.NAME, "password")
        assert username.is_displayed()
        assert password.is_displayed()

    def test_login_as_admin(self, driver, live_server):
        """
        Полноценный вход администратора. Требует запущенного FastAPI с
        пользователем admin/admin123 (см. scripts/seed_data.py в olimp_api).
        """
        driver.get(f"{live_server.url}/login/")
        driver.find_element(By.NAME, "username").send_keys("admin")
        driver.find_element(By.NAME, "password").send_keys("admin123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Управление"))
        )
        assert "Управление" in driver.page_source
