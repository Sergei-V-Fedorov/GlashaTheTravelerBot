"""Реализация команды history"""
import os
from typing import List
from bot_init import bot
from sql import select_query
from config import DB_NAME


async def commands_history(message, db_name: str = DB_NAME) -> None:
    """
    Выводит историю команд
    :param message:
    :param db_name: имя базы данных
    :return:
    """
    if not os.path.exists(db_name):
        await bot.send_message(message.chat.id, "История команд ещё пуста")
        return

    # запрос БД
    history_list = select_query.select_by_user(db_name, message.from_user.id)

    # нет истории команд для user_id
    if not history_list:
        await bot.send_message(message.chat.id, "Сожалеем, Ваша история не сохранена в базе данных")
        return

    text = form_html_text(history_list)
    await bot.send_message(message.chat.id, text, parse_mode="HTML")


def form_html_text(history_result: List['History']) -> str:
    """
    Формируется строка с разметкой html для вывода результатов поиска
    :param history_result:
    :return: html строка
    """
    try:
        result = ["<b>Результаты Ваших предыдущих запросов:</b>\n"]

        for index, history in enumerate(history_result, start=1):
            sep = '\t'
            command_string = f"{sep*3}{index}. {history.datetime} " \
                             f"{history.destination} команда '{history.command}'\n" \
                             f"{sep*6}<i>Найденные гостиницы:</i>\n"
            result.append(command_string)
            for hotel in history.search_result.hotel_list:
                hotel_string = f"{sep*6}<a href='{hotel.web}'>{hotel.name}</a>\n"
                result.append(hotel_string)

        result = ''.join(result)
    except:
        result = "Сожалеем, но во время вывода истории команд возникла ошибка:\n"
    finally:
        return result
