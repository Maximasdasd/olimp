"""
E2E-тесты через Selenium (опционально).

⚠️ ВАЖНО: эти тесты НЕ запускаются вместе с остальными по умолчанию
(в pytest.ini задано addopts = -m "not selenium").

Они требуют:
  * установленного Selenium и webdriver-manager;
  * установленного Chrome/Chromium и chromedriver (webdriver-manager скачает);
  * pytest-django c фикстурой live_server (поднимает реальный сервер на время теста).

В отличие от проекта AutoFleet, здесь вход НЕ зависит от внешнего FastAPI —
Django самодостаточен, поэтому полноценный E2E-логин работает без бэкенда:
достаточно создать пользователя в тестовой БД.

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
@pytest.mark.django_db
class TestSeleniumE2E:
    """Базовые E2E-сценарии. Требуют live_server."""

    def test_olympiad_list_page_loads(self, driver, live_server):
        driver.get(f"{live_server.url}/")
        assert "Олимпиад" in driver.page_source

    def test_login_page_has_form(self, driver, live_server):
        driver.get(f"{live_server.url}/login/")
        username = driver.find_element(By.NAME, "username")
        password = driver.find_element(By.NAME, "password")
        assert username.is_displayed()
        assert password.is_displayed()

    def test_login_as_student(self, driver, live_server, django_user_model):
        """
        Полноценный вход студента. Django самодостаточен, поэтому
        достаточно создать пользователя в тестовой БД.
        """
        django_user_model.objects.create_user(
            username="seleniumuser", password="selenium123",
            role="student", full_name="Селениум Тестовый",
        )
        driver.get(f"{live_server.url}/login/")
        driver.find_element(By.NAME, "username").send_keys("seleniumuser")
        driver.find_element(By.NAME, "password").send_keys("selenium123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # после входа в шапке появляется ссылка на профиль / имя пользователя
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Мой профиль"))
        )
        assert "Мой профиль" in driver.page_source
