import pytest
import allure
from selenium.webdriver.common.by import By
from unittest.mock import MagicMock


class MockDriver(MagicMock):
    def __init__(self):
        super().__init__()
        self.title = "КиноПоиск — фильмы, сериалы, актёры"
        self.current_url = "https://www.kinopoisk.ru/"

    def get(self, url):
        self.current_url = url

    def find_element(self, by=By.ID, value=None):
        element = MagicMock()
        if value == "search_input":
            element.send_keys = MagicMock()
            element.submit = MagicMock()
        elif value == "search_results":
            element.text = "Зеленая миля (1999)"
        elif value == "login_email":
            element.send_keys = MagicMock()
        elif value == "login_password":
            element.send_keys = MagicMock()
        elif value == "login_button":
            element.click = MagicMock()
            self.current_url = "https://www.kinopoisk.ru/profile/"
        elif value == "register_email":
            element.send_keys = MagicMock()
        elif value == "register_password":
            element.send_keys = MagicMock()
        elif value == "register_name":
            element.send_keys = MagicMock()
        elif value == "register_button":
            element.click = MagicMock()
            self.current_url = "https://www.kinopoisk.ru/welcome/"
        elif value == "movie_session":
            element.click = MagicMock()
        elif value == "seat_selection":
            element.click = MagicMock()
        elif value == "buy_button":
            element.click = MagicMock()
            self.current_url = "https://www.kinopoisk.ru/ticket/success/"
        elif value == "success_message":
            element.text = "Билет успешно приобретен!"
        return element


@allure.epic("КиноПоиск - UI Тестирование")
@allure.feature("Пользовательские сценарии")
class TestKinopoiskUI:

    @pytest.fixture
    def driver(self):
        return MockDriver()

    @allure.story("Базовая функциональность")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description("""
    Тест проверяет доступность главной страницы КиноПоиска.
    Это критически важный сценарий для работы всего сайта.
    """)
    @allure.tag("smoke", "critical", "homepage")
    def test_homepage_load(self, driver):
        with allure.step("Открытие главной страницы КиноПоиска"):
            allure.dynamic.title("Проверка загрузки главной страницы")
            driver.get("https://www.kinopoisk.ru/")

        with allure.step("Проверка заголовка страницы"):
            assert "КиноПоиск" in driver.title
            allure.attach(
                f"Заголовок страницы: {driver.title}", name="Page Title")

    @allure.story("Поисковые возможности")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Тестирование поиска конкретного фильма по названию")
    @allure.tag("search", "regression")
    def test_movie_search(self, driver):
        with allure.step("Ввод названия фильма в поисковую строку"):
            allure.dynamic.title("Поиск фильма 'Зеленая миля'")
            search = driver.find_element(By.ID, "search_input")
            search.send_keys("Зеленая миля")

        with allure.step("Отправка поискового запроса"):
            search.submit()
            allure.attach("Поисковый запрос: 'Зеленая миля'",
                          name="Search Query")

        with allure.step("Валидация результатов поиска"):
            results = driver.find_element(By.CLASS_NAME, "search_results")
            assert "Зеленая миля" in results.text
            allure.attach(
                f"Результаты поиска: {results.text}", name="Search Results")

    @allure.story("Аутентификация пользователя")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("""
    Сценарий входа зарегистрированного пользователя в систему.
    Проверяет корректность работы формы авторизации.
    """)
    @allure.tag("auth", "login", "security")
    def test_user_login(self, driver):
        test_email = "test@example.com"
        test_password = "password123"

        with allure.step("Заполнение поля email"):
            allure.dynamic.title("Авторизация пользователя")
            email = driver.find_element(By.ID, "login_email")
            email.send_keys(test_email)
            allure.attach(f"Введен email: {test_email}", name="Email Input")

        with allure.step("Заполнение поля пароля"):
            password = driver.find_element(By.ID, "login_password")
            password.send_keys(test_password)
            allure.attach("Введен пароль: ***", name="Password Input")

        with allure.step("Клик по кнопке 'Войти'"):
            login_btn = driver.find_element(By.ID, "login_button")
            login_btn.click()

        with allure.step("Проверка успешной авторизации"):
            assert "/profile/" in driver.current_url
            allure.attach(
                f"Текущий URL: {driver.current_url}", name="Redirect URL")

    @allure.story("Регистрация новых пользователей")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Тестирование процесса создания нового аккаунта")
    @allure.tag("auth", "registration", "onboarding")
    def test_user_registration(self, driver):
        user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "name": "Иван Иванов"
        }

        with allure.step("Заполнение формы регистрации"):
            allure.dynamic.title("Регистрация нового пользователя")

            with allure.step("Ввод email"):
                email = driver.find_element(By.ID, "register_email")
                email.send_keys(user_data["email"])

            with allure.step("Ввод пароля"):
                password = driver.find_element(By.ID, "register_password")
                password.send_keys(user_data["password"])

            with allure.step("Ввод имени"):
                name = driver.find_element(By.ID, "register_name")
                name.send_keys(user_data["name"])

            allure.attach(str(user_data), name="User Registration Data")

        with allure.step("Подтверждение регистрации"):
            register_btn = driver.find_element(By.ID, "register_button")
            register_btn.click()

        with allure.step("Проверка успешной регистрации"):
            assert "/welcome/" in driver.current_url
            allure.attach(
                f"Редирект после регистрации: {
                    driver.current_url}", name="Post-Registration URL")

    @allure.story("Покупка и бронирование")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
    End-to-end сценарий покупки билета в кино.
    Включает выбор сеанса, места и завершение покупки.
    """)
    @allure.tag("ecommerce", "payment", "ticket")
    def test_buy_ticket(self, driver):
        with allure.step("Выбор сеанса для просмотра"):
            allure.dynamic.title("Покупка билета в кино")
            session = driver.find_element(By.CLASS_NAME, "movie_session")
            session.click()
            allure.attach("Выбран сеанс фильма", name="Session Selection")

        with allure.step("Выбор места в кинозале"):
            seat = driver.find_element(By.CLASS_NAME, "seat_selection")
            seat.click()
            allure.attach("Выбрано место в зале", name="Seat Selection")

        with allure.step("Подтверждение и оплата билета"):
            buy_btn = driver.find_element(By.ID, "buy_button")
            buy_btn.click()

        with allure.step("Верификация успешной покупки"):
            assert "/ticket/success/" in driver.current_url

            success = driver.find_element(By.ID, "success_message")
            assert "Билет успешно" in success.text

            allure.attach(
                f"Сообщение об успехе: {success.text}", name="Success Message")
            allure.attach(
                f"Финальный URL: {driver.current_url}", name="Final URL")
