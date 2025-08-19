import pytest
import allure
from utils.mocks import KinopoiskMockClient


@allure.epic("КиноПоиск - API Тестирование")
@allure.feature("REST API Эндпоинты")
class TestKinopoiskAPI:

    @pytest.fixture
    def api_client(self):
        return KinopoiskMockClient()

    @allure.story("Фильтрация и поиск")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
    Тестирование фильтрации фильмов по году выпуска.
    Проверяет корректность работы параметра 'year' в запросах.
    """)
    @allure.tag("filter", "search", "smoke")
    @allure.link("https://api.kinopoisk.dev/v1.4/movie",
                 name="API Documentation")
    def test_search_movies_by_year(self, api_client):
        with allure.step("Подготовка тестовых данных - фильтр по 2023 году"):
            allure.dynamic.title("Поиск фильмов по году выпуска: 2023")
            test_year = 2023

        with allure.step("Выполнение API запроса с фильтром по году"):
            response = api_client.search_movies(filters={"year": test_year})
            allure.attach(f"Фильтр: year={test_year}", name="Request Filter")

        with allure.step("Проверка статус-кода ответа"):
            assert response.status_code == 200
            allure.attach(
                f"Status Code: {response.status_code}", name="HTTP Status")

        with allure.step("Валидация структуры ответа"):
            data = response.json()
            assert "docs" in data
            assert "total" in data
            assert "limit" in data
            allure.attach(
                f"Найдено фильмов: {data['total']}", name="Total Results")

        with allure.step("Проверка соответствия года у всех фильмов"):
            for movie in data["docs"]:
                assert movie["year"] == test_year
            allure.attach(
                f"Все фильмы соответствуют году: {test_year}",
                name="Year Validation")

    @allure.story("Метаданные фильмов")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Получение информации о наградах и номинациях фильма")
    @allure.tag("metadata", "awards", "movie-info")
    @allure.issue("KP-123", "Награды фильмов")
    def test_movie_awards(self, api_client):
        with allure.step("Подготовка ID тестового фильма"):
            allure.dynamic.title("Получение наград фильма ID: 4664634")
            test_movie_id = 4664634

        with allure.step("Запрос информации о наградах"):
            response = api_client.get_movie_awards(movie_id=test_movie_id)
            allure.attach(f"Movie ID: {test_movie_id}",
                          name="Request Parameter")

        with allure.step("Проверка успешного ответа"):
            assert response.status_code == 200
            data = response.json()

        with allure.step("Валидация структуры данных о наградах"):
            assert "docs" in data
            assert len(data["docs"]) > 0

            award = data["docs"][0]
            assert "nomination" in award
            assert "winning" in award
            assert "movieId" in award

            allure.attach(
                f"Количество наград: {len(data['docs'])}", name="Awards Count")
            allure.attach(
                f"Movie ID в ответе: {award['movieId']}",
                name="Movie ID Validation")

    @allure.story("Фильтрация по рейтингу")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Поиск фильмов с высоким рейтингом (9.0 и выше)")
    @allure.tag("filter", "rating", "quality")
    def test_search_movies_by_rating(self, api_client):
        with allure.step("Установка критерия высокого рейтинга"):
            allure.dynamic.title("Поиск фильмов с рейтингом 9+")
            high_rating = 9

        with allure.step("Выполнение запроса с фильтром по рейтингу"):
            response = api_client.search_movies(
                filters={"rating.kp": high_rating})
            allure.attach(
                f"Фильтр: rating.kp={high_rating}", name="Rating Filter")

        with allure.step("Проверка ответа API"):
            assert response.status_code == 200
            data = response.json()

        with allure.step("Верификация рейтинга у найденных фильмов"):
            for movie in data["docs"]:
                assert movie["rating"]["kp"] == high_rating

            allure.attach(
                f"Найдено фильмов с рейтингом {high_rating}: {len(data['docs'])
                                                              }",
                name="High Rating Movies")

    @allure.story("Системные метаданные")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description(
        "Тестирование фильтрации по дате добавления в базу данных")
    @allure.tag("metadata", "system", "admin")
    @allure.label("owner", "api-team")
    @allure.label("layer", "backend")
    def test_search_by_creation_date(self, api_client):
        with allure.step("Установка тестовой даты добавления"):
            allure.dynamic.title("Поиск по дате добавления: 2025-06-04")
            test_date = "2025-06-04"

        with allure.step("Выполнение запроса с фильтром по дате"):
            response = api_client.search_movies(
                filters={"createdAt": test_date})
            allure.attach(f"Фильтр: createdAt={test_date}", name="Date Filter")

        with allure.step("Анализ ответа сервера"):
            assert response.status_code == 200
            data = response.json()

        with allure.step("Проверка наличия результатов"):
            assert len(data["docs"]) > 0
            allure.attach(
                f"Найдено записей: {len(data['docs'])}", name="Results Count")

        with allure.step("Валидация структуры элементов"):
            item = data["docs"][0]
            assert "createdAt" in item
            assert test_date in item["createdAt"]
            allure.attach(
                f"Дата создания: {item['createdAt']}", name="Creation Date")

    @allure.story("Основная информация о фильмах")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Получение детальной информации о фильме по его идентификатору")
    @allure.tag("movie", "details", "core")
    @allure.link("https://api.kinopoisk.dev/v1.4/movie/{id}",
                 name="Movie Endpoint")
    def test_movie_details_by_id(self, api_client):
        with allure.step("Подготовка тестового ID фильма"):
            allure.dynamic.title("Детали фильма по ID: 4866668")
            test_movie_id = 4866668

        with allure.step("Запрос детальной информации о фильме"):
            response = api_client.get_movie(test_movie_id)
            allure.attach(f"Movie ID: {test_movie_id}",
                          name="Request Parameter")

        with allure.step("Проверка корректности ответа"):
            assert response.status_code == 200
            data = response.json()

        with allure.step("Валидация обязательных полей фильма"):
            assert "id" in data
            assert "name" in data
            assert "rating" in data
            assert "year" in data

        with allure.step("Проверка соответствия ID запроса и ответа"):
            assert data["id"] == test_movie_id
            allure.attach(
                f"Название фильма: {data['name']}", name="Movie Title")
            allure.attach(f"Год выпуска: {data['year']}", name="Release Year")

    @allure.story("Обработка ошибок")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Тестирование обработки несуществующих ресурсов (404 ошибка)")
    @allure.tag("error", "validation", "negative")
    @allure.label("owner", "qa-team")
    @allure.label("priority", "p1")
    def test_movie_not_found(self, api_client):
        with allure.step("Подготовка несуществующего ID фильма"):
            allure.dynamic.title(
                "Обработка 404 ошибки для несуществующего фильма")
            non_existent_id = 999999

        with allure.step("Настройка мока для возврата 404 ошибки"):
            api_client.set_mock_response(
                status_code=404,
                json_data={
                    "error": {
                        "code": 404,
                        "message": "Фильм не найден"
                    }
                }
            )
            allure.attach(
                f"Mock настроен на 404 для ID: {non_existent_id}",
                name="Mock Setup")

        with allure.step("Выполнение запроса к несуществующему ресурсу"):
            response = api_client.get_movie(non_existent_id)

        with allure.step("Проверка кода ошибки"):
            assert response.status_code == 404
            allure.attach(
                f"Получен статус: {response.status_code}", name="Error Status")

        with allure.step("Валидация структуры ошибки"):
            error_data = response.json()
            assert "error" in error_data
            assert error_data["error"]["code"] == 404
            allure.attach(
                f"Сообщение ошибки: {error_data['error']['message']}",
                name="Error Message")

    @allure.story("Пагинация и лимиты")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Тестирование механизма пагинации и ограничения выборки")
    @allure.tag("pagination", "performance", "optimization")
    @allure.issue("KP-789", "Пагинация результатов")
    @allure.parent_suite("API Tests")
    def test_search_pagination(self, api_client):
        with allure.step("Установка параметров пагинации"):
            allure.dynamic.title(
                "Тестирование пагинации: страница 2, лимит 10")
            test_page = 2
            test_limit = 10

        with allure.step("Выполнение запроса с пагинацией"):
            response = api_client.search_movies(
                filters={"year": 2020},
                page=test_page,
                limit=test_limit
            )
            allure.attach(
                f"Параметры: page={test_page}, limit={test_limit}",
                name="PaginationParams")

        with allure.step("Проверка успешного ответа"):
            assert response.status_code == 200
            data = response.json()

        with allure.step("Валидация параметров пагинации в ответе"):
            assert "page" in data
            assert "pages" in data
            assert "limit" in data
            assert data["page"] == test_page
            assert data["limit"] == test_limit

        with allure.step("Проверка размера возвращаемой выборки"):
            assert len(data["docs"]) <= test_limit
            allure.attach(
                f"Текущая страница: {data['page']}", name="Current Page")
            allure.attach(
                f"Всего страниц: {data['pages']}", name="Total Pages")
            allure.attach(
                f"Элементов на странице: {
                    len(data['docs'])}", name="Items per Page")
