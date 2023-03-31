"""Реализация команды bestdeal"""
from telebot import asyncio_filters
from bot_init import bot, UserStates
from config import MAX_HOTELS
import commands.cancel


async def ask_min_cost(message):
    """
    Устанавливает состояние в min_price
    :param message:
    :return:
    """
    await bot.set_state(message.from_user.id, UserStates.min_price, message.chat.id)
    await bot.send_message(message.chat.id, "Введите минимальную стоимость номера за ночь")


@bot.message_handler(state=[UserStates.min_price, UserStates.max_price], is_digit=True)
async def get_room_cost_range(message):
    """
    Шаг 6. Получение диапазона цен за номер
    """
    current_state = await bot.get_state(message.from_user.id, message.chat.id)
    price = int(message.text)
    # минимальная цена за номер
    if current_state == "UserStates:min_price":
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["min_price"] = price
        await bot.set_state(message.from_user.id, UserStates.max_price, message.chat.id)
        await bot.send_message(message.chat.id, "Введите максимальную стоимость номера за ночь")
    # максимальная цена за номер
    elif current_state == "UserStates:max_price":
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if price >= data["min_price"]:  # максимальная цена больше или равна минимальной
                data["max_price"] = price
                await bot.set_state(message.from_user.id, UserStates.min_distance, message.chat.id)
                await bot.send_message(message.chat.id,
                                       "Введите минимальное расстояние гостиницы до центра "
                                       "города в километрах")
            else:
                await bot.send_message(message.chat.id,
                                       "Максимальная стоимость номера должна быть больше или "
                                       "равна минимальной стоимости.\nПовторите ввод")


@bot.message_handler(state=[UserStates.min_distance, UserStates.max_distance], is_digit=True)
async def get_distance_range(message):
    """
    Шаг 7. Получение диапазона удаленности гостиницы от центра города
    """
    current_state = await bot.get_state(message.from_user.id, message.chat.id)
    distance = int(message.text)
    # минимальное расстояние от центра
    if current_state == "UserStates:min_distance":
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["min_distance"] = distance
        await bot.set_state(message.from_user.id, UserStates.max_distance, message.chat.id)
        await bot.send_message(message.chat.id,
                               "Введите максимальное расстояние гостиницы до центра "
                               "города в километрах")
    # максимальное расстояние от центра
    elif current_state == "UserStates:max_distance":
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            # максимальное расстояние больше или равно минимальному
            if distance >= data["min_distance"]:
                data["max_distance"] = distance
                await bot.set_state(message.from_user.id, UserStates.hotel_number, message.chat.id)
                await bot.send_message(message.chat.id,
                                       f"Максимальное количество выводимых отелей "
                                       f"(не более {MAX_HOTELS}):")
            else:
                await bot.send_message(message.chat.id,
                                       "Максимальное расстояние должно быть больше или "
                                       "равно минимальному.\nПовторите ввод")

# register filters
bot.add_custom_filter(asyncio_filters.StateFilter(bot))
