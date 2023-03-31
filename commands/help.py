"""Реализация команды help"""
from bot_init import bot


@bot.message_handler(commands=["help"])
async def show_help(message):
    """
    Показывает доступные команды бота
    """
    text = """<b>Доступные команды:</b>
    /help - Помощь по командам бота
    /highprice - Вывод самых дорогих отелей в городе
    /lowprice - Вывод самых дешёвых отелей в городе
    /bestdeal - Вывод отелей, наиболее подходящих по цене и расположению от центра
    /history - Вывод истории поиска отелей
    /cancel - Отмена текущего поиска"""
    await bot.send_message(message.chat.id, text, parse_mode="HTML")
