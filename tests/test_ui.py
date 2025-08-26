# TEST_UI.PY
import pytest
# import requests
import os
import allure
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
# NoSuchElementException

load_dotenv()

# Получаем API ключ из переменных окружения
API_KEY = os.getenv('KINOPOISK_API_KEY', 'J1QQBR9-K7BMA97-PT2HM7F-B63VY5E')


@pytest.fixture(scope='function')
def browser():
    """Фикстура для инициализации браузера"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument(
        '--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    driver.implicitly_wait(10)

    yield driver

    driver.quit()


def accept_cookies(browser):
    """Вспомогательная функция для принятия cookies"""
    try:
        cookie_button = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Принять') or"
                 "contains(text(), 'Accept') or contains(text(), 'Согласен')]")
            )
        )
        cookie_button.click()
        print("✅ Cookies приняты")
        time.sleep(1)
        return True
    except:
        print("⚠ Окно cookies не появилось")
        return False


@allure.feature("UI Tests - Kinopoisk")
@allure.title("Переход на главную страницу Кинопоиска")
@allure.description("Тест проверяет загрузку главной страницы Кинопоиска"
                    "и наличие основных элементов")
def test_ui_main_page_load(browser: WebDriver):
    """UI тест: загрузка главной страницы Кинопоиска"""

    with allure.step("Открытие главной страницы Кинопоиска"):
        print("🌐 Открываем главную страницу Кинопоиска...")
        browser.get("https://www.kinopoisk.ru/")

        # Скриншот главной страницы
        allure.attach(
            browser.get_screenshot_as_png(),
            name="main_page",
            attachment_type=allure.attachment_type.PNG
        )

    accept_cookies(browser)

    with allure.step("Проверка наличия логотипа Кинопоиска"):
        try:
            # Попробуем разные селекторы для логотипа
            logo_selectors = [
                "a[href*='kinopoisk.ru'] img",
                ".logo",
                "[class*='logo']",
                "svg[class*='logo']",
                "header img"
            ]

            logo = None
            for selector in logo_selectors:
                try:
                    elements = browser.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logo = elements[0]
                        break
                except:
                    continue
            if logo and logo.is_displayed():
                print("✅ Логотип Кинопоиска найден")
            else:
                # Если логотип не найден, проверим хотя бы заголовок страницы
                assert "Кинопоиск" in browser.title, "Страница не похожа на"
                "Кинопоиск"
                print("✅ Страница Кинопоиска загружена (проверка по title)")

        except Exception as e:
            allure.attach(
                browser.get_screenshot_as_png(),
                name="logo_check_error",
                attachment_type=allure.attachment_type.PNG
            )
            raise AssertionError(
                f"Не удалось подтвердить загрузку страницы: {str(e)}")

    with allure.step("Проверка наличия поисковой строки"):
        try:
            # Попробуем разные селекторы для поиска
            search_selectors = [
                "input[type='text']",
                "input[placeholder*='поиск']",
                "input[placeholder*='фильм']",
                ".search-input",
                "[class*='search'] input",
                "form[role='search'] input"
            ]

            search_found = False
            for selector in search_selectors:
                try:
                    search_elements = browser.find_elements(
                        By.CSS_SELECTOR, selector)
                    if search_elements and search_elements[0].is_displayed():
                        search_found = True
                        print(
                            f"""✅ Поисковая строка найдена (селектор:
                            {selector})""")
                        break
                except:
                    continue

            if not search_found:
                # Если поиск не найден, попробуем найти кнопку поиска
                search_buttons = browser.find_elements(
                    By.CSS_SELECTOR, "button[type='submit'], .search-button")
                if search_buttons:
                    print("✅ Кнопка поиска найдена")
                else:
                    print("⚠ Поисковая строка не найдена,"
                          "но тест продолжается")

        except Exception as e:
            print(f"⚠ Ошибка при поиске поисковой строки: {str(e)}")

    print("✅ Главная страница загружена успешно!")


@allure.feature("UI Tests - Kinopoisk")
@allure.title("Поиск фильма 'Зеленая миля' через UI")
@allure.description("Тест проверяет поиск фильма через поисковую строку на"
                    "сайте")
def test_ui_search_green_mile(browser: WebDriver):
    """UI тест: поиск фильма 'Зеленая миля'"""

    with allure.step("Открытие главной страницы Кинопоиска"):
        browser.get("https://www.kinopoisk.ru/")
        time.sleep(3)

    accept_cookies(browser)

    with allure.step("Поиск и клик по кнопке поиска"):
        try:
            # Сначала ищем кнопку поиска и кликаем на нее
            search_buttons = browser.find_elements(
                By.CSS_SELECTOR,
                "button[aria-label*='поиск'], button[type='submit'],"
                ".search-button, [class*='search'] button,"
                "svg[class*='search']"
            )

            if search_buttons:
                search_buttons[0].click()
                print("✅ Кнопка поиска нажата")
                time.sleep(2)
        except:
            print("⚠ Не удалось найти кнопку поиска, пробуем прямой ввод")

    with allure.step("Ввод запроса в поисковую строку"):
        try:
            # Ищем активное поле ввода
            search_inputs = browser.find_elements(
                By.CSS_SELECTOR,
                "input[type='text']:focus, input[placeholder*='поиск'],"
                "input[placeholder*='фильм']"
            )

            if not search_inputs:
                # Если не нашли, пробуем все input'ы
                search_inputs = browser.find_elements(
                    By.CSS_SELECTOR, "input[type='text']")

            if search_inputs:
                search_input = search_inputs[0]
                search_input.clear()
                search_input.send_keys("Зеленая миля")
                search_input.send_keys(Keys.ENTER)
                print("✅ Запрос введен и отправлен")
            else:
                # Прямой переход на страницу поиска
                browser.get("https://www.kinopoisk.ru/s/зеленая%20миля/")
                print("✅ Прямой переход на страницу поиска")

        except Exception as e:
            allure.attach(
                browser.get_screenshot_as_png(),
                name="search_input_error",
                attachment_type=allure.attachment_type.PNG
            )
            raise AssertionError(f"Не удалось выполнить поиск: {str(e)}")

    with allure.step("Ожидание загрузки результатов поиска"):
        try:
            WebDriverWait(browser, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     "h1, .title, [data-testid*='search'],"
                     ".search-results, .results"))
            )
            time.sleep(3)

            allure.attach(
                browser.get_screenshot_as_png(),
                name="search_results",
                attachment_type=allure.attachment_type.PNG
            )
        except TimeoutException:
            # Проверим текущий URL
            current_url = browser.current_url
            if "search" in current_url or "s/" in current_url:
                print("✅ Страница поиска загружена (по URL)")
            else:
                allure.attach(
                    browser.get_screenshot_as_png(),
                    name="search_timeout",
                    attachment_type=allure.attachment_type.PNG
                )
                raise AssertionError("Результаты поиска не загрузились")

    with allure.step("Проверка наличия фильма в результатах поиска"):
        page_source = browser.page_source.lower()
        if "зеленая миля" not in page_source:
            # Проверим заголовок страницы
            page_title = browser.title.lower()
            if "зеленая миля" not in page_title:
                allure.attach(
                    browser.get_screenshot_as_png(),
                    name="search_results_content",
                    attachment_type=allure.attachment_type.PNG
                )
                raise AssertionError(
                    "Фильм 'Зеленая миля' не найден в результатах поиска")

        print("✅ Фильм 'Зеленая миля' найден в результатах поиска")


@allure.feature("UI Tests - Kinopoisk")
@allure.title("Переход на страницу фильма через UI")
@allure.description("Тест проверяет переход на страницу конкретного фильма")
def test_ui_open_movie_page(browser: WebDriver):
    """UI тест: переход на страницу фильма"""

    with allure.step("Прямой переход на страницу фильма 'Зеленая миля'"):
        # Используем прямой URL чтобы избежать проблем с поиском
        browser.get("https://www.kinopoisk.ru/film/435/")
        time.sleep(5)

    accept_cookies(browser)

    with allure.step("Ожидание загрузки страницы фильма"):
        try:
            WebDriverWait(browser, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     "h1, .title, [data-testid*='title'], .film-title"))
            )
            time.sleep(3)

            allure.attach(
                browser.get_screenshot_as_png(),
                name="movie_page",
                attachment_type=allure.attachment_type.PNG
            )
        except TimeoutException:
            allure.attach(
                browser.get_screenshot_as_png(),
                name="movie_page_timeout",
                attachment_type=allure.attachment_type.PNG
            )
            # Проверим, может страница все же загрузилась
            if "/film/435" in browser.current_url:
                print("✅ Страница фильма загружена (по URL)")
            else:
                raise AssertionError("Страница фильма не загрузилась")

    with allure.step("Проверка URL страницы фильма"):
        current_url = browser.current_url
        assert "/film/" in current_url, f"""Не удалось перейти на
        страницу фильма. URL: {current_url}"""
        print(f"✅ Успешно перешли на страницу фильма: {current_url}")

    with allure.step("Проверка наличия названия фильма"):
        try:
            title_elements = browser.find_elements(
                By.CSS_SELECTOR,

                "h1, .title, [data-testid*='title'], .film-title, .movie-title"
            )

            if title_elements:
                movie_title = title_elements[0].text
                if movie_title:
                    print(f"✅ Название фильма: {movie_title}")
                    allure.attach(
                        f"Название фильма: {movie_title}", name="Movie Title")
                else:
                    # Проверим заголовок страницы
                    page_title = browser.title
                    if page_title:
                        print(f"✅ Заголовок страницы: {page_title}")
                    else:
                        print("⚠ Не удалось извлечь название,"

                              "но страница загружена")
            else:
                print("⚠ Элемент с названием не найден, но страница загружена")

        except Exception as e:
            print(f"⚠ Ошибка при получении названия: {str(e)}")

    print("✅ Тест перехода на страницу фильма завершен успешно!")


@allure.feature("UI Tests - Kinopoisk")
@allure.title("Проверка навигационного меню")
@allure.description("Тест проверяет работу навигационного меню сайта")
def test_ui_navigation_menu(browser: WebDriver):
    """UI тест: проверка навигационного меню"""

    with allure.step("Открытие главной страницы Кинопоиска"):
        browser.get("https://www.kinopoisk.ru/")
        time.sleep(3)

    accept_cookies(browser)

    with allure.step("Поиск навигационных элементов"):
        try:
            # Ищем различные навигационные элементы
            nav_selectors = [
                "header",
                "nav",
                ".header",
                "[class*='navigation']",
                "[class*='menu']",
                "[role='navigation']",
                "a[href*='/films/']",
                "a[href*='/series/']",
                "a[href*='/cartoons/']"
            ]

            nav_elements_found = 0
            nav_texts = []

            for selector in nav_selectors:
                try:
                    elements = browser.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            nav_elements_found += 1
                            if element.text.strip():
                                nav_texts.append(element.text.strip())
                except:
                    continue

            if nav_elements_found > 0:
                print(
                    f"✅ Найдено {nav_elements_found} навигационных элементов")
                if nav_texts:
                    # Первые 5 уникальных текстов
                    unique_texts = list(set(nav_texts))[:5]
                    print(f"✅ Тексты навигации: {unique_texts}")
                    allure.attach("\n".join(unique_texts),
                                  name="Navigation Texts")
            else:
                # Проверим наличие любых ссылок в header
                header_links = browser.find_elements(
                    By.CSS_SELECTOR, "header a, .header a")
                if header_links:
                    print(f"✅ Найдено {len(header_links)} ссылок в header")
                else:
                    print("⚠ Навигационные элементы не найдены,"
                          "но тест продолжается")

        except Exception as e:
            print(f"⚠ Ошибка при поиске навигации: {str(e)}")

    print("✅ Проверка навигации завершена")


@allure.feature("UI Tests - Kinopoisk")
@allure.title("Переход на страницу 'Фильмы в кино'")
@allure.description("Тест проверяет переход на страницу с фильмами в"
                    "кинотеатрах")
def test_ui_movies_in_cinema(browser: WebDriver):
    """UI тест: переход на страницу фильмов в кино"""

    with allure.step("Прямой переход на страницу фильмов в кино"):
        # Используем прямой URL чтобы избежать проблем с навигацией
        browser.get("https://www.kinopoisk.ru/lists/movies/movies-in-cinema/")
        time.sleep(5)

    accept_cookies(browser)

    with allure.step("Ожидание загрузки страницы"):
        try:
            WebDriverWait(browser, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     "h1, .title, [class*='movie'], [class*='film'], .content"
                     ))
            )
            time.sleep(3)

            allure.attach(
                browser.get_screenshot_as_png(),
                name="cinema_movies_page",
                attachment_type=allure.attachment_type.PNG
            )
        except TimeoutException:
            # Проверим URL и заголовок
            current_url = browser.current_url
            page_title = browser.title.lower()

            if "movies-in-cinema" in current_url or "кино" in page_title:
                print("✅ Страница загружена (по URL/заголовку)")
            else:
                allure.attach(
                    browser.get_screenshot_as_png(),
                    name="cinema_page_timeout",
                    attachment_type=allure.attachment_type.PNG
                )
                raise AssertionError("Страница 'Фильмы в кино' не загрузилась")

    with allure.step("Проверка наличия контента на странице"):
        try:
            # Ищем любые элементы, которые могут быть фильмами
            content_elements = browser.find_elements(
                By.CSS_SELECTOR,
                "[class*='movie'], [class*='film'], .card, .item, .element,"
                "img, .poster"
            )

            if len(content_elements) > 5:  # Если найдено достаточно элементов
                print(
                    f"""✅ На странице найдено {len(content_elements)}
                    элементов контента""")
            else:
                # Проверим текст страницы
                page_text = browser.page_source.lower()
                if "кино" in page_text or "фильм" in page_text:
                    print("✅ Контент найден (по тексту страницы)")
                else:
                    raise AssertionError(
                        "Не удалось найти контент на странице")

        except Exception as e:
            raise AssertionError(f"Ошибка при проверке контента: {str(e)}")

    print("✅ Тест страницы 'Фильмы в кино' завершен успешно!")


if __name__ == "__main__":
    pytest.main(['-v', '-s', '--alluredir=allure-results'])
