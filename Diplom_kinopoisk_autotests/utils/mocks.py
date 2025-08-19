from unittest.mock import MagicMock
# from datetime import datetime


class MockDriver(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = "КиноПоиск - фильмы и сериалы"
        self.current_url = "https://www.kinopoisk.ru/"
        self.find_element.return_value = MagicMock(text="")
        self.execute_script.return_value = None

    def get(self, url):
        self.current_url = url
        return None

    def set_mock_element(self, text="", **kwargs):
        mock = MagicMock()
        mock.text = text
        for key, value in kwargs.items():
            setattr(mock, key, value)
        self.find_element.return_value = mock
        return mock


class KinopoiskMockClient:
    def __init__(self):
        self.mock_response = None
        self.reset_mocks()

    def reset_mocks(self):
        self.mock_response = MagicMock()
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = {
            "docs": [
                {
                    "id": 123,
                    "name": "Интерстеллар",
                    "year": 2014,
                    "rating": {"kp": 8.6},
                    "createdAt": "2020-01-01T00:00:00.000Z"
                },
                {
                    "id": 124,
                    "name": "Начало",
                    "year": 2010,
                    "rating": {"kp": 8.7},
                    "createdAt": "2020-01-02T00:00:00.000Z"
                }
            ],
            "total": 2,
            "limit": 10,
            "page": 1,
            "pages": 1
        }

    def set_mock_response(self, status_code=200, json_data=None):
        self.mock_response = MagicMock()
        self.mock_response.status_code = status_code
        if json_data:
            self.mock_response.json.return_value = json_data
        else:
            self.mock_response.json.return_value = {
                "error": {
                    "code": status_code,
                    "message": "Default error message"
                }
            }
        return self.mock_response

    def search_movies(self, query="", filters=None, page=1, limit=10):
        # Мок для поиска с фильтрами
        if filters:
            if "year" in filters:
                year = filters["year"]
                mock_data = {
                    "docs": [
                        {
                            "year": year,
                            "name": f"Фильм {year} года",
                            "id": i
                        }
                        for i in range(1, 4)
                    ],
                    "total": 100,
                    "limit": limit,
                    "page": page,
                    "pages": 10
                }
                self.mock_response.json.return_value = mock_data

            elif "rating.kp" in filters:
                rating = filters["rating.kp"]
                mock_data = {
                    "docs": [
                        {
                            "id": 4866668,
                            "name": "BTS Permission To Dance: On "
                            "Stage — Seoul",
                            "year": 2022,
                            "rating": {
                                "kp": rating,
                                "imdb": 7.9
                            },
                            "votes": {
                                "kp": 1412
                            }
                        }
                    ],
                    "total": 1,
                    "limit": limit,
                    "page": page,
                    "pages": 1
                }
                self.mock_response.json.return_value = mock_data

            elif "createdAt" in filters:
                mock_data = {
                    "docs": [
                        {
                            "id": 166128951,
                            "title": "Эни (корейская анимация)",
                            "createdAt": "2025-06-04T22:19:41.962Z",
                            "updatedAt": "2025-06-04T22:19:41.962Z"
                        }
                    ],
                    "total": 34355,
                    "limit": limit,
                    "page": page,
                    "pages": 11452
                }
                self.mock_response.json.return_value = mock_data
            else:
                # Дефолтный ответ для других фильтров
                self.mock_response.json.return_value = {
                    "docs": [],
                    "total": 0,
                    "limit": limit,
                    "page": page,
                    "pages": 0
                }
        else:
            # Ответ для поиска без фильтров
            self.mock_response.json.return_value = {
                "docs": [
                    {
                        "id": 123,
                        "name": "Интерстеллар",
                        "year": 2014,
                        "rating": {"kp": 8.6},
                        "createdAt": "2020-01-01T00:00:00.000Z"
                    }
                ],
                "total": 1,
                "limit": limit,
                "page": page,
                "pages": 1
            }

        return self.mock_response

    def get_movie(self, movie_id):
        if self.mock_response.status_code == 200:
            movie_mock = MagicMock()
            movie_mock.status_code = 200
            movie_mock.json.return_value = {
                "id": movie_id,
                "name": "Интерстеллар",
                "year": 2014,
                "rating": {"kp": 8.6, "imdb": 8.6},
                "description": "Фильм о путешествиях в космосе"
            }
            return movie_mock
        return self.mock_response

    def get_movie_awards(self, movie_id):
        awards_mock = MagicMock()
        awards_mock.status_code = 200
        awards_mock.json.return_value = {
            "docs": [
                {
                    "nomination": {
                        "award": {"title": "Оскар", "year": 2024},
                        "title": "Лучший грим и прически"
                    },
                    "winning": False,
                    "movieId": movie_id
                }
            ],
            "total": 28097,
            "limit": 3,
            "page": 1,
            "pages": 9366
        }
        return awards_mock

    def get_similar_movies(self, movie_id):
        similar_mock = MagicMock()
        similar_mock.status_code = 200
        similar_mock.json.return_value = {
            "docs": [
                {"id": 125, "name": "Гравитация", "rating": {"kp": 7.8}},
                {"id": 126, "name": "Марсианин", "rating": {"kp": 8.0}}
            ],
            "total": 2,
            "limit": 10,
            "page": 1,
            "pages": 1
        }
        return similar_mock
