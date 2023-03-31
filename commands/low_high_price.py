"""Реализация команд lowprice и highprice"""
import datetime as dt
from telebot import asyncio_filters
from bot_init import bot, UserStates
from hotel_requests import get_destination_list
from config import MAX_SLEEPS, MAX_HOTELS, MAX_PHOTOS
from util import gen_markup, output_response, button_name
from custom_filters import IsDate
from commands.best_deal import ask_min_cost
import commands.cancel


async def start_request(message):
    """
    Шаг 1. Запрос пункта назначения
    """
    await bot.set_state(message.from_user.id, UserStates.city, message.chat.id)
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["command"] = message.text[1:]
        data["datetime"] = dt.datetime.now()
        if data["command"] == "lowprice":
            data["sort_order"] = "PRICE"
        elif data["command"] == "highprice":
            data["sort_order"] = "PRICE_HIGHEST_FIRST"
        elif data["command"] == "bestdeal":
            data["sort_order"] = "DISTANCE_FROM_LANDMARK"
    await bot.send_message(message.chat.id,
                           "Введите город, для которого будет проводиться поиск отелей")


@bot.message_handler(state=UserStates.city)
async def get_city(message) -> None:
    """
    Шаг 2. Получение пункта назначения. Поиск совпадений. Вывод результатов
    """
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["city"] = message.text

    # получения списка городов
    city_list = get_destination_list(data["city"])

    # если совпадений не найдено, то выход
    if not city_list:
        await bot.send_message(
            message.chat.id, "По Вашему запросу ничего не найдено. \n"
            "Проверьте правильность написания пункта назначения и "
            "повторно вызовите команду")
        await bot.delete_state(message.from_user.id, message.chat.id)
        return

    await bot.set_state(message.from_user.id, UserStates.destination_id, message.chat.id)
    await bot.send_message(message.chat.id,
                           f"По Вашему запросу найдено {len(city_list)} варианта(ов). \n ")
    city_list.append({"Нет нужного": "Cancel"})
    await bot.send_message(message.chat.id, "Выберите подходящий город из списка",
                           reply_markup=gen_markup(city_list))


@bot.callback_query_handler(func=None, state=UserStates.destination_id)
async def callback_query(call):
    """
    Шаг 3. Получение ID пункта назначения. Запрос даты заезда
    """
    if call.data == "Cancel":
        await bot.delete_state(call.from_user.id)
        await bot.send_message(call.message.chat.id, "Поиск был отменён. Введите команду")
    else:
        async with bot.retrieve_data(call.from_user.id) as data:
            data["destination_id"] = call.data
            destination = await button_name(call.message, call.data)
            if destination:
                data["city"] = destination
        await bot.set_state(call.from_user.id, UserStates.check_in)
        await bot.send_message(call.message.chat.id, "Введите дату заезда (гггг-мм-дд):")


@bot.message_handler(state=[UserStates.check_in, UserStates.check_out], is_date=True)
async def get_dates(message):
    """
    Шаг 4. Получение даты заезда и выезда
    """
    current_state = await bot.get_state(message.from_user.id, message.chat.id)
    # дата заезда
    if current_state == "UserStates:check_in":
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["check_in"] = message.text
        await bot.set_state(message.from_user.id, UserStates.check_out, message.chat.id)
        await bot.send_message(message.chat.id, "Введите дату выезда (гггг-мм-дд):")
    # дата выезда
    elif current_state == "UserStates:check_out":
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            date_in = dt.datetime.strptime(data["check_in"], "%Y-%m-%d")
            date_out = dt.datetime.strptime(message.text, "%Y-%m-%d")
            if date_out > date_in:  # дата выезда больше даты заезда
                data["check_out"] = message.text
                await bot.set_state(message.from_user.id, UserStates.adults, message.chat.id)
                await bot.send_message(message.chat.id,
                                       f"Введите количество спальных мест в номере "
                                       f"(не более {MAX_SLEEPS}):")
            else:
                await bot.send_message(message.chat.id,
                                       "Дата выезда должна быть больше даты заезда.\n"
                                       "Повторите ввод")


@bot.message_handler(state=[UserStates.check_in, UserStates.check_out], is_date=False)
async def date_incorrect(message):
    """
    Шаг 4. Проверка правильности ввода даты заезда и выезда
    """
    await bot.send_message(message.chat.id, "Формат даты (гггг-мм-дд):")


@bot.message_handler(state=UserStates.adults, is_digit=True)
async def get_sleeps(message):
    """
    Шаг 5. Получение количества спальных мест в номере
    """
    num_sleeps = int(message.text)
    if num_sleeps <= MAX_SLEEPS:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["adults"] = num_sleeps
            if data["command"] == "bestdeal":  # переход к шагу 6
                await ask_min_cost(message)
            else:  # переход к шагу 8
                await bot.set_state(message.from_user.id, UserStates.hotel_number, message.chat.id)
                await bot.send_message(message.chat.id,
                                       f"Максимальное количество выводимых отелей "
                                       f"(не более {MAX_HOTELS}):")
    else:
        await bot.send_message(message.chat.id,
                               f"Количество спальных мест не должно превышать {MAX_SLEEPS}.\n"
                               f"Повторите ввод")


@bot.message_handler(state=[UserStates.adults, UserStates.min_price, UserStates.max_price,
                            UserStates.min_distance, UserStates.max_distance,
                            UserStates.hotel_number, UserStates.photo_number], is_digit=False)
async def number_incorrect(message):
    """
    Шаги 5-8, 10. Проверка правильности ввода целых чисел
    """
    await bot.send_message(message.chat.id, "Введите целое число:")


@bot.message_handler(state=UserStates.hotel_number, is_digit=True)
async def get_hotel_number(message):
    """
    Шаг 8. Получение количества гостиниц, для которых выводить результаты поиска
    """
    hotel_number = int(message.text)
    if hotel_number <= MAX_HOTELS:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['hotel_number'] = hotel_number
            await bot.set_state(message.from_user.id, UserStates.need_photos, message.chat.id)
            answer_buttons = [{"Да": "yes"}, {"Нет": "no"}]
            await bot.send_message(message.chat.id, "Выводить фотографии для каждого отеля?",
                                   reply_markup=gen_markup(answer_buttons))
    else:
        await bot.send_message(message.chat.id, f"Количество выводимых отелей не должно превышать "
                                                f"{MAX_HOTELS}.\nПовторите ввод")


@bot.callback_query_handler(func=None, state=UserStates.need_photos)
async def yes_no_query(call):
    """
    Шаг 9. Запрос о выводе фотографий для гостиницы
    """
    if call.data == "yes":
        await bot.set_state(call.from_user.id, UserStates.photo_number)
        await bot.send_message(call.message.chat.id,
                               f"Введите количество фотографий (не более {MAX_PHOTOS}):")
    elif call.data == "no":
        async with bot.retrieve_data(call.from_user.id) as data:
            data["photo_number"] = 0
        await output_response(call.message)
    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)


@bot.message_handler(state=UserStates.photo_number, is_digit=True)
async def get_photo_number(message):
    """
    Шаг 10. Получение количества фотографий гостиниц
    """
    photo_number = int(message.text)
    if photo_number <= MAX_PHOTOS:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photo_number'] = photo_number
        await output_response(message)
    else:
        await bot.send_message(message.chat.id,
                               f"Количество фотографий для каждой гостиницы не должно "
                               f"превышать {MAX_PHOTOS}.\nПовторите ввод")


# register filters
bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(asyncio_filters.IsDigitFilter())
bot.add_custom_filter(IsDate())
