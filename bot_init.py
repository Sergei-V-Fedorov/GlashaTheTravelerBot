"""Инициализация асинхронного бота"""
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup
from config import TOKEN


# User States
class UserStates(StatesGroup):
    """Описывает состояния бота"""
    city = State()
    destination_id = State()
    check_in = State()
    check_out = State()
    adults = State()
    min_price = State()
    max_price = State()
    min_distance = State()
    max_distance = State()
    hotel_number = State()
    need_photos = State
    photo_number = State()


# словарь, в котором будут храниться пользовательские запросы,
# ключ = user_id, значение = instance UserQuery
user_queries = {}

bot = AsyncTeleBot(TOKEN, state_storage=StateMemoryStorage())
