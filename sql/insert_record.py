"""Добавление записи в БД"""
import sqlite3


def insert_record_query(db_name: str, user_data: 'UserQuery') -> None:
    """
    Добавление записи в таблицы БД
    :param db_name: имя файла БД
    :param user_data: результаты поиска гостиниц
    :return:
    """
    try:
        connection = sqlite3.connect(db_name, timeout=20)
        cursor = connection.cursor()

        # Добавляем данные в таблицу requests
        insert_query = f"""INSERT INTO requests (userId, command, requestDate, destination)
        VALUES ({user_data.user_id}, '{user_data.command}', '{user_data.datetime}',
        '{user_data.destination}');"""
        cursor.execute(insert_query)
        request_id = cursor.lastrowid

        # Добавляем данные в таблицу hotels
        for hotel_info in user_data.search_result.hotel_list:
            # проверка наличия гостиницы в таблице
            select_query = """
            SELECT hotelId FROM hotels
            WHERE (name == ? AND link == ?)"""
            cursor.execute(select_query, (hotel_info.name, hotel_info.web))

            hotel_id = cursor.fetchone()
            # если нет, то добавляем в таблицу
            if hotel_id is None:
                insert_query = """INSERT INTO hotels VALUES (NULL, ?, ?);"""
                cursor.execute(insert_query, (hotel_info.name, hotel_info.web))
                hotel_id = cursor.lastrowid
            else:  # если есть, то берем id отеля
                hotel_id = hotel_id[0]

            # Добавляем данные о запросе и отелях в request_results
            insert_query = """INSERT INTO request_results VALUES (NULL, ?, ?);"""
            cursor.execute(insert_query, (request_id, hotel_id))

        connection.commit()
        cursor.close()
    except sqlite3.Error as error:
        if connection:
            connection.rollback()
        print("Ошибка при добавлении записи в таблицу БД", error)
    finally:
        if connection:
            connection.close()
