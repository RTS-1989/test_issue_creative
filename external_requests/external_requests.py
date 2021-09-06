import os
import requests

from dotenv import load_dotenv
# API key нужно разместить в файле .env, чтобы скрыть его от посторонних.
# Также в случае смены ключа нужно будет сменить только значение переменной окружения.
load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


# Класс не наследуется от другого класса. Нужно убрать ().
class GetWeatherRequest:
    """
    Выполняет запрос на получение текущей погоды для города
    """

    def __init__(self):
        """
        Инициализирует класс
        """
        self.session = requests.Session()

    @staticmethod
    def get_weather_url(city):
        """
        Генерирует url включая в него необходимые параметры
        Args:
            city: Город
        Returns:

        """
        # Можно url написать в одну строку.
        # В случае если длина строки нарушает pep8 можер ставить знак переноса строки.
        url = 'https://api.openweathermap.org/data/2.5/weather?units=metric&q=' + city + '&appid=' + WEATHER_API_KEY
        return url

    def send_request(self, url):
        """
        Отправляет запрос на сервер
        Args:
            url: Адрес запроса
        Returns:

        """
        r = self.session.get(url)
        if r.status_code != 200:
            r.raise_for_status()
        return r

    # Можно сделать static
    @staticmethod
    def get_weather_from_response(response):
        """
        Достает погоду из ответа
        Args:
            response: Ответ, пришедший с сервера
        Returns:

        """
        data = response.json()
        return data['main']['temp']

    def get_weather(self, city):
        """
        Делает запрос на получение погоды
        Args:
            city: Город
        Returns:

        """
        url = GetWeatherRequest.get_weather_url(city)
        r = self.send_request(url)
        if r is None:
            return None
        else:
            weather = GetWeatherRequest.get_weather_from_response(r)
            return weather


# Класс не наследуется от другого класса. Нужно убрать ().
class CheckCityExisting:
    """
    Проверка наличия города (запросом к серверу погоды)
    """

    def __init__(self):
        """
        Инициализирует класс
        """
        self.session = requests.Session()

    # Можно сделать static
    @staticmethod
    def get_weather_url(city):
        """
        Генерирует url включая в него необходимые параметры
        Args:
            city: Город
        Returns:

        # Можно url написать в одну строку.
        # В случае если длина строки нарушает pep8 можер ставить знак переноса строки.
        """
        url = 'https://api.openweathermap.org/data/2.5/weather?units=metric&q=' + city + '&appid=' + WEATHER_API_KEY
        return url

    def send_request(self, url):
        """
        Отправляет запрос на сервер
        Args:
            url: Адрес запроса
        Returns:

        """
        r = self.session.get(url)
        return r

    def check_existing(self, city):
        """
        Проверяет наличие города
        Args:
            city: Название города
        Returns:

        """
        url = CheckCityExisting.get_weather_url(city)
        r = self.send_request(url)
        if r.status_code == 404:
            return False
        if r.status_code == 200:
            return True
