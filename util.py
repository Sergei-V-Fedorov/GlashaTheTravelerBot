"""Дополнительные функции для работы бота"""
import os
from telebot import types
from bot_init import bot, user_queries
from query_classes import UserQuery
from hotel_requests import get_response
from config import DB_NAME
import sql


def gen_markup(button_list: list, width: int = 3):
    """
    Формирует инлайн клавиатуру
    :param button_list: список словарей [{"key_1": "value_1"}, ...]
    :param width: кол-во кнопок с строке
    :return: InlineKeyboardMarkup c кнопками
    """
    markup = types.InlineKeyboardMarkup(row_width=width)
    inline_key_buttons = [types.InlineKeyboardButton(text=key, callback_data=value)
                          for item in button_list
                          for key, value in item.items()]
    markup.add(*inline_key_buttons)
    return markup


async def output_response(message) -> None:
    """
    Вывод ответа пользователю на его запрос
    :param message:
    :return:
    """
    await bot.send_message(message.chat.id, "Ждите... Выполняется поиск...")
    # запрос пользователя
    if message.from_user.is_bot:
        user_id = message.chat.id
    else:
        user_id = message.from_user.id

    # retrieve_data to user_query
    user_query = UserQuery()
    user_query.user_id = user_id
    async with bot.retrieve_data(user_id, message.chat.id) as data:
        user_query.destination_id = data["destination_id"]
        user_query.destination = data["city"]
        user_query.sort_order = data["sort_order"]
        user_query.check_in = data["check_in"]
        user_query.check_out = data["check_out"]
        user_query.adults = data["adults"]
        user_query.hotel_number = data["hotel_number"]
        user_query.picture_number = data["photo_number"]
        user_query.min_price = data.get("min_price")
        user_query.max_price = data.get("max_price")
        user_query.min_distance = data.get("min_distance")
        user_query.max_distance = data.get("max_distance")
        user_query.command = data["command"]
        user_query.datetime = data["datetime"].strftime("%Y-%m-%d %H:%M")

    await bot.delete_state(user_id, message.chat.id)
    user_queries[user_id] = user_query

    # результаты поиска отелей
    user_query.search_result = get_response(user_query=user_query)

    # формируем ответ бота
    bot_text = form_html_text(user_query.search_result)
    await bot.send_message(message.chat.id, bot_text, parse_mode="HTML")

    # запись результатов в БД
    if not os.path.exists(DB_NAME):
        sql.create_database.create_tables(DB_NAME)
    sql.insert_record.insert_record_query(DB_NAME, user_query)


def form_html_text(search_result: 'QueryResponse') -> str:
    """
    Формируется строка с разметкой html для вывода результатов поиска
    :param search_result:
    :return: html строка
    """
    if search_result.status_code == 200 and not search_result.error_message:
        # не найдены гостиницы, соответствующие критериям поиска
        if not search_result.hotel_list:
            return "<b>Сожалеем, но по введённым критериям гостиниц не найдено</b>"

        # гостинцы найдены
        result = ["<b>По Вашему запросу найдены следующие гостиницы:</b>\n"]

        # добавление информации об отеле
        for index, item in enumerate(search_result.hotel_list, start=1):
            substring = "{span}{num}. {hotel_name}\n".format(span='\t'*3, num=index,
                                                             hotel_name=item.name) + \
                     "{span}<a href='{url}'>Веб-сайт отеля</a>\n".format(span='\t'*6,
                                                                         url=item.web) + \
                     "{span}Расстояние до центра: {dist}\n".format(span='\t'*6,
                                                                   dist=item.dist_from_center) + \
                     "{span}Цена за ночь: {price} руб.\n".format(span='\t'*6,
                                                                 price=item.price) + \
                     "{span}Цена за время пребывания: {price} руб.\n".format(span='\t'*6,
                                                                             price=item.total_price)
            result.append(substring)

            # добавление фотографий отеля
            if item.photos:
                result.append("{span}<i>Фотографии отеля:</i>\n".format(span='\t'*6))
                for photo in item.photos:
                    result.append("{span}<a href='{url}'>Фото</a>\n".format(span='\t'*6, url=photo))

        result = ''.join(result)
    else:
        result = "Сожалеем, но во время поиска возникла ошибка:\n" + \
                 "Код запроса: {}\n".format(search_result.status_code) + \
                 "Ошибка: {}".format(search_result.error_message)
    return result


async def button_name(message, data: str) -> str:
    """
    Возвращает текст, написанный на нажатой кнопке
    :param message:
    :param data: значение, которое ищется
    :return: текст, написанный на кнопке
    """
    result = ""
    try:
        inline_keyboard = message.json["reply_markup"]["inline_keyboard"]
        row_number = len(inline_keyboard)
        for row in range(row_number):
            for column in range(len(inline_keyboard[row])):
                if inline_keyboard[row][column]["callback_data"] == data:
                    result = inline_keyboard[row][column]["text"]
                    return result
    except Exception as exc:
        print("Не удалось получить клавиатуру. Ошибка", exc)
    finally:
        return result
