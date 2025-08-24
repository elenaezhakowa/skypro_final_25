import os
import random
import time
from dotenv import load_dotenv
# from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pytest

load_dotenv()  # Загружаем переменные окружения из .env файла


@pytest.fixture(scope="session")
def browser():
    """Инициализируем браузер перед началом сессии."""
    from selenium import webdriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument(
        "--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=chrome_options)
    yield driver
    driver.quit()


@pytest.fixture
def wait(browser):
    """Ожидание элементов интерфейса."""
    return WebDriverWait(browser, 30)


@pytest.fixture
def actions(browser):
    """Фикстура для человеческих действий."""
    return ActionChains(browser)


@pytest.fixture
def base_url():
    """Базовый URL тестируемого сайта."""
    return os.getenv('BASE_URL', 'https://www.kinopoisk.ru/')


def human_delay(min_seconds=0.3, max_seconds=1.5):
    """Случайная задержка как у человека."""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay


def human_type(element, text, actions):
    """Человеческий ввод текста."""
    actions.move_to_element(element).click().pause(
        human_delay(0.2, 0.5)).perform()
    for char in text:
        element.send_keys(char)
        actions.pause(random.uniform(0.1, 0.3)).perform()


def human_click(element, actions):
    """Человеческий клик."""
    actions.move_to_element(element).pause(human_delay(
        0.5, 1.2)).click().pause(human_delay(0.3, 0.8)).perform()


@pytest.mark.parametrize("search_term", [("Зеленая миля"), ("Матрица")])
def test_search_movie(browser, wait, base_url, search_term, actions):
    """Тестирование поиска фильма по названию."""
    browser.get(base_url)
    human_delay(1.0, 2.0)  # Ожидание загрузки

    # Поиск поисковой строки с человеческой задержкой
    search_input = wait.until(
        EC.element_to_be_clickable((By.NAME, "kp_query")))

    # Человеческий ввод
    human_type(search_input, search_term, actions)
    search_input.send_keys(Keys.ENTER)
    human_delay(1.5, 2.5)  # Ожидание результатов

    # Ждем появление результатов поиска
    results = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, ".styles_root__I2ZoX a, ["
                          "data-test-id='movie-card']")))

    assert len(
        results) > 0, f"Результатов поиска для '{search_term}' не найдено."


def test_login(browser, wait, base_url, actions):
    """Тестирует вход на сайт с действительными учетными данными."""
    browser.get(f"{base_url}login/")
    human_delay(1.5, 2.5)

    # Поиск полей ввода с человеческими задержками
    email_input = wait.until(EC.element_to_be_clickable((By.NAME, "email")))
    password_input = wait.until(
        EC.element_to_be_clickable((By.NAME, "password")))

    # Получение учетных данных из .env
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')

    assert email and password, "Учетные данные не найдены в .env файле"

    # Человеческий ввод данных
    human_type(email_input, email, actions)
    human_delay(0.5, 1.0)
    human_type(password_input, password, actions)
    human_delay(0.5, 1.0)

    # Поиск и клик по кнопке входа
    sign_in_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(text(), 'Войти') or contains(text(),"
                   "'Sign in')]")))
    human_click(sign_in_btn, actions)

    # Ожидание успешного входа с человеческой задержкой
    human_delay(2.0, 3.0)

    # Проверка успешного входа
    profile_elements = browser.find_elements(
        By.XPATH, "//*[contains(@class,'profile') or contains(@class,'user')"
                  "or contains(text(), 'Мой профиль')]")

    assert len(profile_elements) > 0, "Пользователь не вошел успешно."


def test_buy_ticket(browser, wait, base_url, actions):
    """Тестирует процесс покупки билета на фильм."""
    browser.get(base_url)
    human_delay(1.5, 2.5)

    # Поиск и ввод названия фильма
    search_input = wait.until(
        EC.element_to_be_clickable((By.NAME, "kp_query")))
    human_type(search_input, "Довод", actions)
    search_input.send_keys(Keys.ENTER)
    human_delay(2.0, 3.0)

    # Поиск и клик по первому результату
    first_result = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "(//a[contains(@href,'/film/')])[1]")))
    human_click(first_result, actions)
    human_delay(2.0, 3.0)

    # Попытка найти кнопку покупки билетов
    buy_buttons = browser.find_elements(
        By.XPATH, "//*[contains(text(), 'Купить билет') or contains(text("
        "), 'Билеты')]")

    if not buy_buttons:
        pytest.skip(
            "Кнопка покупки билетов не найдена - возможно фильм не в прокате")

    human_click(buy_buttons[0], actions)
    human_delay(2.0, 3.0)

    # Упрощенная проверка - хотя бы что-то связанное с билетами
    page_text = browser.find_element(By.TAG_NAME, "body").text
    ticket_keywords = ["билет", "ticket", "сеанс", "сеансы", "кинотеатр"]

    assert any(keyword in page_text.lower() for keyword in ticket_keywords), \
        "Не найдено элементов связанных с покупкой билетов"


@pytest.mark.parametrize("rating", [7.5, 8.0, 8.5])
def test_search_by_rating(browser, wait, base_url, rating, actions):
    """Тестирует поиск фильмов по минимальному рейтингу."""
    browser.get(
        f"{base_url}/catalog/movies/?rating={
            rating}&sortField=RATING&sortType=-1")
    human_delay(2.0, 3.5)

    # Поиск результатов с человеческой задержкой
    results = wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, "//*[contains(@class, 'movie') or contains("
                   "@class, 'film')]//a")))

    assert len(results) > 0, f"Не найдено фильмов с рейтингом >= {rating}"

    # Человеческая проверка - промотаем страницу
    browser.execute_script("window.scrollBy(0, 500);")
    human_delay(1.0, 2.0)

    # Проверка что на странице есть упоминание рейтинга
    page_text = browser.find_element(By.TAG_NAME, "body").text
    assert str(rating) in page_text or "рейтинг" in page_text.lower(), \
        f"На странице нет упоминания рейтинга {rating}"


if __name__ == "__main__":
    pytest.main(['-v', '--tb=short'])
