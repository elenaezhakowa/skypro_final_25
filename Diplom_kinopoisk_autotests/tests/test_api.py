import pytest
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


@pytest.fixture(scope='session')
def browser():
    """Фикстура для инициализации браузера"""
    print("🚀 Запускаем браузер...")

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument(
        "--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    # Убираем признаки автоматизации
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver',"
        "{get: () => undefined})")

    print("✅ Браузер запущен!")
    yield driver

    driver.quit()
    print("✅ Браузер закрыт!")


@pytest.fixture(scope='session')
def wait(browser):
    return WebDriverWait(browser, 20)


@pytest.fixture(scope='function')
def actions(browser):
    return ActionChains(browser)


def human_delay(min_seconds=0.5, max_seconds=2.0):
    """Случайная задержка как у человека"""
    delay = random.uniform(min_seconds, max_seconds)
    return delay


def human_type(element, text, actions, min_delay=0.1, max_delay=0.3):
    """Человеческий ввод текста с случайными задержками"""
    actions.move_to_element(element).click().pause(
        human_delay(0.2, 0.5)).perform()

    for char in text:
        element.send_keys(char)
        actions.pause(random.uniform(min_delay, max_delay)).perform()


def human_click(element, actions):
    """Человеческий клик с задержкой"""
    actions.move_to_element(element).pause(human_delay(
        0.3, 1.0)).click().pause(human_delay(0.5, 1.5)).perform()


def wait_for_human_like_loading(wait, actions, min_time=1.0, max_time=3.0):
    """Ожидание загрузки с человеческой задержкой"""
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    actions.pause(human_delay(min_time, max_time)).perform()


def test_ui_search_green_mile(browser, wait, actions):
    """UI тест: поиск Зеленой мили в браузере"""
    print("🌐 Открываем КиноПоиск...")
    browser.get("https://www.kinopoisk.ru/")

    # Ждем загрузки с человеческой задержкой
    wait_for_human_like_loading(wait, actions, 2.0, 4.0)

    # Поиск поисковой строки
    search_input = None
    search_selectors = [
        (By.NAME, "kp_query"),
        (By.CSS_SELECTOR, "input[type='search']"),
        (By.CSS_SELECTOR, "input[type='text']"),
        (By.XPATH, "//input[@placeholder='Поиск...']"),
        (By.XPATH, "//input[@placeholder='Search...']")
    ]

    for by, selector in search_selectors:
        elements = browser.find_elements(by, selector)
        if elements:
            search_input = elements[0]
            print(f"🔍 Найдена поисковая строка: {selector}")
            break

    assert search_input is not None, "Поисковая строка не найдена"

    # Человеческий ввод текста
    print("⌨️ Человеческий ввод 'Зеленая миля'...")
    human_type(search_input, "Зеленая миля", actions)

    # Человеческий клик Enter
    actions.send_keys(Keys.ENTER).pause(human_delay(1.0, 2.0)).perform()

    # Ждем результаты с человеческой задержкой
    print("⏳ Ожидаем результаты поиска...")
    wait_for_human_like_loading(wait, actions, 2.0, 4.0)

    # Проверяем результаты
    page_text = browser.find_element(By.TAG_NAME, "body").text
    assert "Зеленая миля" in page_text or "Green Mile" in page_text, \
        "Фильм 'Зеленая миля' не найден в результатах"

    print("✅ UI поиск выполнен успешно!")
    browser.save_screenshot("ui_search_results.png")


def test_ui_high_rated_movies(browser, wait, actions):
    """UI тест: поиск высокорейтинговых фильмов"""
    print("⭐ Ищем высокорейтинговые фильмы через UI...")

    # Переходим в раздел "Лучшие фильмы"
    browser.get("https://www.kinopoisk.ru/lists/movies/top250/")

    # Человеческая задержка перед взаимодействием
    wait_for_human_like_loading(wait, actions, 2.0, 3.0)

    # Промотаем немного страницу как человек
    actions.send_keys(Keys.PAGE_DOWN).pause(human_delay(0.5, 1.5)).perform()
    actions.send_keys(Keys.PAGE_DOWN).pause(human_delay(0.5, 1.5)).perform()

    # Ищем фильмы с высоким рейтингом
    movie_cards = browser.find_elements(
        By.CSS_SELECTOR, ".styles_root__tlAh7, .movie-item, .film-card,"
                         "[class*='card']")

    if not movie_cards:
        # Альтернативный поиск
        movie_cards = browser.find_elements(
            By.XPATH, "//a[contains(@href, '/film/')]")

    assert len(movie_cards) > 0, "Не найдено фильмов в топе"

    # Человеческая проверка - промотаем еще
    actions.send_keys(Keys.PAGE_DOWN).pause(human_delay(1.0, 2.0)).perform()

    # Проверяем, что есть фильмы с высоким рейтингом
    page_text = browser.find_element(By.TAG_NAME, "body").text
    high_rated_keywords = ["8.", "9.", "рейтинг", "rating", "IMDb", "КП"]

    has_high_rated = any(
        keyword in page_text for keyword in high_rated_keywords)
    assert has_high_rated, "Не найдено признаков высоких рейтингов"

    print(f"✅ Найдено {len(movie_cards)} фильмов в топе")
    browser.save_screenshot("ui_top_movies.png")


def test_ui_movies_by_year(browser, wait, actions):
    """UI тест: поиск фильмов по году"""
    print("📅 Ищем новые фильмы через UI...")

    browser.get("https://www.kinopoisk.ru/lists/movies/2023/")

    # Человеческая задержка
    wait_for_human_like_loading(wait, actions, 2.0, 3.0)

    # Промотаем страницу
    actions.send_keys(Keys.PAGE_DOWN).pause(human_delay(1.0, 2.0)).perform()
    actions.send_keys(Keys.PAGE_DOWN).pause(human_delay(0.5, 1.5)).perform()

    # Проверяем, что мы на странице фильмов 2023 года
    page_text = browser.find_element(By.TAG_NAME, "body").text
    assert "2023" in page_text or "2023" in browser.current_url, \
        "Не удалось перейти на страницу фильмов 2023 года"

    # Ищем фильмы
    movie_elements = browser.find_elements(
        By.XPATH, "//a[contains(@href, '/film/')]")
    assert len(movie_elements) > 0, "Не найдено фильмов 2023 года"

    # Человеческое взаимодействие - наведем на первый фильм
    if movie_elements:
        actions.move_to_element(movie_elements[0]).pause(
            human_delay(0.5, 1.5)).perform()

    print(f"✅ Найдено {len(movie_elements)} фильмов 2023 года")
    browser.save_screenshot("ui_2023_movies.png")


def test_ui_popular_movies(browser, wait, actions):
    """UI тест: проверка популярных фильмов"""
    print("🎬 Проверяем популярные фильмы через UI...")

    browser.get("https://www.kinopoisk.ru/")

    # Человеческая задержка для осмотра страницы
    wait_for_human_like_loading(wait, actions, 2.0, 4.0)

    # Промотаем главную страницу как человек
    for _ in range(3):
        actions.send_keys(Keys.PAGE_DOWN).pause(
            human_delay(1.0, 2.0)).perform()

    # Ищем блоки с популярными фильмами
    popular_sections = [
        "Сейчас в кино",
        "Популярные фильмы",
        "Лучшие фильмы",
        "Новые фильмы",
        "Рекомендуем посмотреть"
    ]

    page_text = browser.find_element(By.TAG_NAME, "body").text
    has_popular = any(section in page_text for section in popular_sections)

    assert has_popular, "Не найдено разделов с популярными фильмами"

    # Ищем сами фильмы
    movie_links = browser.find_elements(
        By.XPATH, "//a[contains(@href, '/film/')]")
    assert len(movie_links) > 5, "Слишком мало фильмов на главной странице"

    # Человеческое взаимодействие - промотаем назад к верху
    actions.send_keys(Keys.HOME).pause(human_delay(1.0, 2.0)).perform()

    print(f"✅ Найдено {len(movie_links)} фильмов на главной странице")
    browser.save_screenshot("ui_popular_movies.png")


def test_ui_movie_categories(browser, wait, actions):
    """UI тест: проверка различных категорий"""
    print("🏷️ Проверяем категории фильмов через UI...")

    categories_to_test = [
        "https://www.kinopoisk.ru/genre/12/",  # Комедии
        "https://www.kinopoisk.ru/genre/6/",   # Боевики
        "https://www.kinopoisk.ru/genre/3/",   # Драмы
    ]

    for i, category_url in enumerate(categories_to_test):
        print(f"   📁 Переходим в категорию {i+1}/{len(categories_to_test)}...")
        browser.get(category_url)

        # Человеческая задержка для изучения страницы
        wait_for_human_like_loading(wait, actions, 2.0, 3.0)

        # Промотаем страницу
        actions.send_keys(Keys.PAGE_DOWN).pause(
            human_delay(1.0, 2.0)).perform()

        # Проверяем загрузку категории
        body_text = browser.find_element(By.TAG_NAME, "body").text
        assert len(
            body_text) > 1000
        f"Страница категории не загрузилась: {category_url}"

        # Ищем фильмы в категории
        movies = browser.find_elements(
            By.XPATH, "//a[contains(@href, '/film/')]")
        assert len(
            movies) > 0, f"Не найдено фильмов в категории: {category_url}"

        # Человеческая пауза между категориями
        if i < len(categories_to_test) - 1:
            actions.pause(human_delay(1.5, 3.0)).perform()

        print(f"   ✅ Категория {i+1}: {len(movies)} фильмов")

    browser.save_screenshot("ui_categories.png")


if __name__ == "__main__":
    pytest.main(['-v', '-s'])
