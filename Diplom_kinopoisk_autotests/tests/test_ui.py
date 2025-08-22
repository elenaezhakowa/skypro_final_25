import os
from dotenv import load_dotenv
# Import для работы с выпадающим списком
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pytest


load_dotenv()  # Загружаем переменные окружения из .env файла


@pytest.fixture(scope="session")
def browser():
    """Инициализируем браузер перед началом сессии."""
    from selenium import webdriver
    driver = webdriver.Chrome()
    yield driver
    driver.quit()


@pytest.fixture
def wait(browser):
    """Ожидание элементов интерфейса."""
    return WebDriverWait(browser, 30)  # Таймаут увеличен до 30 секунд


@pytest.fixture
def base_url():
    """Базовый URL тестируемого сайта."""
    return os.getenv('BASE_URL', 'https://www.kinopoisk.ru/')


@pytest.mark.parametrize(
    "search_term",
    [
        ("Зеленая миля"),  # Используем реальный фильм
        ("Матрица")
    ],
)
def test_search_movie(browser, wait, base_url, search_term):
    """
    Тестирование поиска фильма по названию.
    """
    browser.get(base_url)
    search_input = browser.find_element(By.NAME, "kp_query")
    search_input.clear()
    search_input.send_keys(search_term + Keys.ENTER)

    # Ждем появление результатов поиска
    wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, ".styles_root__I2ZoX a")))
    results = browser.find_elements(By.CSS_SELECTOR, ".styles_root__I2ZoX a")
    assert len(
        results) > 0, f"Результатов поиска для '{search_term}' не найдено."


def test_login(browser, wait, base_url):
    """
    Тестирует вход на сайт с действительными учетными данными.
    """
    browser.get(f"{base_url}/account/login/")
    email_input = browser.find_element(By.NAME, "email")
    password_input = browser.find_element(By.NAME, "password")
    sign_in_btn = browser.find_element(
        By.XPATH, "//button[contains(text(), 'Войти')]")

    credentials = {
        "email": os.getenv('EMAIL'),  # Используем настоящие данные из .env
        "password": os.getenv('PASSWORD')
    }
    email_input.send_keys(credentials["email"])
    password_input.send_keys(credentials["password"])
    sign_in_btn.click()

    # Ждем успешного входа
    wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//span[contains(@class,'headerProfileLink__nickname')]")))
    profile_link = browser.find_element(
        By.XPATH, "//span[contains(@class,'headerProfileLink__nickname')]")
    assert profile_link.is_displayed(), "Пользователь не вошел успешно."


def test_buy_ticket(browser, wait, base_url):
    """
    Тестирует процесс покупки билета на фильм.
    """
    browser.get(f"{base_url}")
    search_input = browser.find_element(By.NAME, "kp_query")
    search_input.send_keys("Довод" + Keys.ENTER)

    # Ждём первую ссылку на фильм
    wait.until(EC.presence_of_element_located(
        (By.XPATH, "(//a[contains(@href,'/film/')])[1]")))
    first_result = browser.find_element(
        By.XPATH, "(//a[contains(@href,'/film/')])[1]")
    first_result.click()

    # Ждём появления кнопки "Купить билеты"
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//a[contains(text(),'Купить билеты')]")))
    buy_tickets_btn = browser.find_element(
        By.XPATH, "//a[contains(text(),'Купить билеты')]")
    buy_tickets_btn.click()

    # Выбираем ближайший подходящий сеанс
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//select[@name='session']")))
    session_select = Select(browser.find_element(
        By.XPATH, "//select[@name='session']"))  # Используем Select
    session_select.select_by_visible_text("Сегодня вечером")

    # Ждём возможность выбрать лучшие места
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//input[@type='checkbox' and @value='best-seat']")))
    best_seats_checkbox = browser.find_element(
        By.XPATH, "//input[@type='checkbox' and @value='best-seat']")
    best_seats_checkbox.click()

    # Продолжаем оплату
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(text(),'Продолжить оплату')]")))
    proceed_to_payment = browser.find_element(
        By.XPATH, "//button[contains(text(),'Продолжить оплату')]")
    proceed_to_payment.click()

    # Подтверждаем успешную покупку
    wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//p[contains(text(),'Оплата билетов')]")))
    payment_confirmation = browser.find_element(
        By.XPATH, "//p[contains(text(),'Оплата билетов')]").text
    assert "Оплата билетов" in payment_confirmation
    "Покупка билета завершилась неудачно"


@pytest.mark.parametrize("rating", [7.5, 8.0, 8.5])
def test_search_by_rating(browser, wait, base_url, rating):
    """
    Тестирует поиск фильмов по минимальному рейтингу.
    """
    browser.get(
        f"""{base_url}/catalog/films/?ratingFrom={rating}&sortField=RATING&
        sortType=-1""")
    wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, "//div[@class='styles_root__I2ZoX']//a")))
    results = browser.find_elements(
        By.XPATH, "//div[@class='styles_root__I2ZoX']//a")
    for result in results[:5]:  # Проверяем первые пять фильмов
        title_and_rating = result.text.split("\n")
        if len(title_and_rating) > 1:
            try:
                film_rating = float(title_and_rating[-1].split()[0])
                assert film_rating >= rating, \
                    f"""Фильм {title_and_rating[0]} имеет рейтинг
                    ниже заданного ({rating})"""
            except ValueError:
                continue  # Пропустить фильмы без рейтинга
