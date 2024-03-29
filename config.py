"""Конфигурация бота, параметров запроса, БД"""
TOKEN = "insert_your_bot_token"

# Константы
MAX_SLEEPS = 4  # Количество мест в номере
MAX_HOTELS = 10  # Максимальное количество гостиниц в результате поиска
MAX_PHOTOS = 5  # Максимальное количество фотографий в результате поиска

# заголовок запроса сервера rapidapi
HEADERS = {"X-RapidAPI-Key": "insert_your_rapidapi_key",
           "X-RapidAPI-Host": "hotels4.p.rapidapi.com"}

# локаль и валюта
LOCALE = "ru_RU"
CURRENCY = "RUB"

# URL для запроса по поиску города
URL_CITY = "https://hotels4.p.rapidapi.com/locations/v2/search"
# URL для запроса для получения списка отелей
URL_HOTEL = "https://hotels4.p.rapidapi.com/properties/list"
# URL для запроса для получения фотографий отеля
URL_PHOTO = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

DB_NAME = "sql/glasha.db"
DB_LIMIT = 5
