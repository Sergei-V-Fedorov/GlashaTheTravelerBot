"""Пользовательские фильтры для ввода корректных данных"""
import datetime as dt
from telebot import asyncio_filters, types


class IsDate(asyncio_filters.SimpleCustomFilter):
    """ Фильтр для проверки является строка датой"""
    key = 'is_date'

    @staticmethod
    def check(message: types.Message) -> bool:
        return is_date_valid(message.text)


async def is_date_valid(date_string: str) -> bool:
    """ Проверяет правильность даты """
    try:
        dt.datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False
