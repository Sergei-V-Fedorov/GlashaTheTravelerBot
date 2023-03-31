"""Получение запроса от БД"""
import sqlite3
from typing import List
from query_classes import History, Hotel, QueryResponse
from config import DB_LIMIT


def select_by_user(db_name: str, user_id: int, limit: int = DB_LIMIT) -> List['History']:
    """
    Выбираем из БД записи, соответствующие user_id
    :param db_name: имя файла БД
    :param user_id: ID пользователя
    :param limit: максимальное кол-во выводимых результатов
    :return: список списков [(параметры команды), [(параметры отеля),]]
    """
    try:
        result = []
        connection = sqlite3.connect(db_name, timeout=20)
        cursor = connection.cursor()
        # get query about request
        select_query = """
        SELECT 
            requestId, command, destination, requestDate
        FROM requests
        WHERE userId == ?
        ORDER BY requestDate DESC
        LIMIT ?;"""

        cursor.execute(select_query, (user_id, limit))
        req = cursor.fetchall()

        # нет записи
        if not req:
            return result

        # get query for hotels
        for item in req:
            select_query = """
            SELECT hotels.hotelId, name, link FROM hotels 
                JOIN request_results as res ON res.hotelId == hotels.hotelId
                JOIN requests as req ON req.requestId == res.requestId
            WHERE req.requestId == ?;"""
            hotel_res = cursor.execute(select_query, (item[0],))

            # заполняем поля класса History
            user_query = History()
            user_query.command = item[1]
            user_query.destination = item[2]
            user_query.datetime = item[3]
            hotel_list = QueryResponse()
            for hotel_info in hotel_res:
                hotel = Hotel(hotel_info[0])
                hotel.set_name(hotel_info[1])
                hotel.set_cite(hotel_info[2])
                hotel_list.add_hotel(hotel)
            user_query.search_result = hotel_list
            result.append(user_query)

        connection.commit()
        cursor.close()

    except sqlite3.Error as error:
        if connection:
            connection.rollback()
        print("Ошибка при обращении к таблицам БД", error)
    finally:
        if connection:
            connection.close()
        return result
