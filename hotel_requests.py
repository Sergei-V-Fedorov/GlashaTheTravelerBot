"""Функции для получения запросов от rapidapi.com"""
from typing import List, Callable
from datetime import datetime
from requests.exceptions import HTTPError
import requests
import query_classes
from query_classes import UserQuery
from config import HEADERS, URL_HOTEL, URL_PHOTO, URL_CITY, LOCALE, CURRENCY


def get_destination_list(destination: str, for_url: str = URL_CITY) -> List[dict]:
    """
    Получает список городов, совпадающих с destination
    :param destination: название города
    :param for_url: url запроса
    :return: список словарей {"city_name": "city_id"}
    """
    query_str = {}
    query_str["query"] = destination
    query_str["locale"] = LOCALE
    query_str["currency"] = CURRENCY
    response = requests.get(for_url, headers=HEADERS, params=query_str)
    city_group = response.json()["suggestions"][0]
    destination_list = [{entity["name"]: entity["destinationId"]}
                        for entity
                        in city_group["entities"]]
    return destination_list


def form_querystring(user_query: UserQuery) -> dict:
    """
    Формирует строку запроса для получения списка отелей
    :param user_query: пользовательский запрос (UserQuery class)
    :return: строка запроса для поиска отелей (dict)
    """
    query_str = {}
    query_str["locale"] = LOCALE
    query_str["currency"] = CURRENCY
    query_str["pageSize"] = "25"
    query_str["destinationId"] = user_query.destination_id
    query_str["checkIn"] = user_query.check_in
    query_str["checkOut"] = user_query.check_out
    query_str["adults1"] = str(user_query.adults)
    query_str["sortOrder"] = user_query.sort_order
    return query_str


def get_response(user_query: UserQuery, for_url=URL_HOTEL) -> 'QueryResponse':
    """
        Формирует ответ по пользовательскому запросу
        :param user_query: пользовательский запрос
        :param for_url: url для формирования запроса на получение списка отелей
        :return: QueryResponse class, содержащий список отелей,
        удовлетворяющих пользовательскому запросу
    """
    hotel_info = query_classes.QueryResponse()
    # выполнять запросы, пока список гостиниц не будет равен запрашиваемому кол-ву
    try:
        query_str = form_querystring(user_query)
        page_number = 1
        while len(hotel_info.hotel_list) < user_query.hotel_number:
            query_str["pageNumber"] = page_number
            response = requests.get(for_url, headers=HEADERS, params=query_str)
            print(response.status_code)
            print("processing page", page_number)
            hotel_info.status_code = response.status_code
            response.raise_for_status()

            search_results = response.json()["data"]["body"]["searchResults"]
            # убираем отели, в которых не указана стоимость проживания
            hotel_list = list(
                filter(lambda result: result.get("ratePlan") is not None,
                       search_results["results"]))

            # для команды bestdeal применяем фильтр диапазона значений
            if user_query.command == "bestdeal":
                range_filter = generate_filter(min_cost=user_query.min_price,
                                               max_cost=user_query.max_price,
                                               min_dist=user_query.min_distance,
                                               max_dist=user_query.max_distance)
                hotel_list = list(
                    filter(range_filter, hotel_list))

            # заносим в hotel_info информацию о каждом отеле в списке
            hotel_list = hotel_list[0:user_query.hotel_number]
            for item in hotel_list:
                hotel = query_classes.Hotel(item["id"])
                hotel.set_name(item["name"])
                hotel.set_cite("https://www.hotels.com/ho" + str(hotel.id))
                hotel.set_distance(item["landmarks"][0]["distance"])
                hotel.set_price(item["ratePlan"]["price"]["exactCurrent"])
                number_days = datetime.strptime(user_query.check_out, "%Y-%m-%d") - \
                              datetime.strptime(user_query.check_in, "%Y-%m-%d")
                hotel.set_total_price(round(number_days.days * hotel.price, 2))
                hotel_info.add_hotel(hotel)
                # если требуется выводить фотографии
                if user_query.picture_number:
                    photo_list = get_hotel_photo(hotel.id, user_query.picture_number)
                    if not photo_list:
                        hotel_info.error_message = "Возникла ошибка при получении фотографий"
                    else:
                        for photo in photo_list:
                            hotel.add_photo(photo)
            # если есть результаты на других страницах, берем их, иначе покидаем цикл
            page_number += 1
            # 25 - максимальное кол-во результатов на странице
            if page_number > search_results["totalCount"] // 25:
                break

    except HTTPError as http_err:
        hotel_info.error_message = f"HTTP error occurred: {http_err}"
    except requests.exceptions.JSONDecodeError as err:
        hotel_info.error_message = f"JSON error occurred: {err}"
    except KeyError as err:
        hotel_info.error_message = f"Отсутствуют данные по ключу: {err}"
    except Exception as err:
        hotel_info.error_message = f"Error occurred: {err.__repr__()}"
    finally:
        return hotel_info


def get_hotel_photo(hotel_id: int, photos_number: int, for_url=URL_PHOTO) -> List[str]:
    """
    Возвращает N фотографий отеля
    :param hotel_id: ID отеля
    :param photos_number: число фотографий
    :param for_url: url запроса
    :return:
    """
    querystring = {}
    querystring["id"] = hotel_id
    try:
        request = requests.get(for_url, headers=HEADERS, params=querystring)
        hotel_photos = request.json()["hotelImages"]
        photos_number = min(photos_number, len(hotel_photos))
        result = []
        for photo in hotel_photos[:photos_number]:
            result.append(photo["baseUrl"].format(size='y'))
        return result
    except:
        return []


def generate_filter(min_cost: int = 0, max_cost: int = 25000,
                    min_dist: int = 0, max_dist: int = 25) -> Callable:
    """
    Генератор фильтра по проверке отеля критериям расстояния от центра и стоимости.
    :param min_cost: минимальная стоимость номера.
    :param max_cost: максимальная стоимость номера.
    :param min_dist: минимальное расстояние от центра.
    :param max_dist: максимальное расстояние от центра.
    :return:
    """
    def distance_price_filter(hotel_info: dict) -> bool:
        """
        Проверяет удовлетворяет ли гостиница условиям по стоимости и удаленности от центра города.
        :param hotel_info: информация об отеле.
        :return: bool
        """
        if min_cost <= hotel_info["ratePlan"]["price"]["exactCurrent"] <= max_cost:
            distance_from_center = hotel_info["landmarks"][0]["distance"].split()[0]
            distance_from_center = distance_from_center.replace(',', '.')
            result = False
            try:
                distance_from_center = float(distance_from_center)
                if min_dist <= distance_from_center <= max_dist:
                    result = True
            except ValueError:
                result = False
        else:
            result = False
        return result
    return distance_price_filter
