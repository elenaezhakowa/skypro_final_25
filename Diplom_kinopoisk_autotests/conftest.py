import pytest
import allure
from utils.browser_utils import create_stealth_browser
from utils.mocks import KinopoiskMockClient
from selenium.common.exceptions import WebDriverException


@pytest.fixture
def driver():
    """Фикстура для stealth браузера"""
    driver = None
    try:
        driver = create_stealth_browser()
        yield driver

    except WebDriverException as e:
        pytest.fail(f"Не удалось инициализировать WebDriver: {e}")

    finally:
        if driver:
            try:
                driver.quit()
            except WebDriverException:
                pass


@pytest.fixture
def api_client():
    """Фикстура для мок-клиента API Кинопоиска"""
    client = KinopoiskMockClient()
    client.reset_mocks()
    yield client
    client.reset_mocks()
