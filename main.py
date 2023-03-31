"""Главный модуль для запуска бота по поиску отелей @GlashaTheTravelerBot"""
import asyncio
from bot_init import bot
import commands


@bot.message_handler(commands=["lowprice", "highprice", "bestdeal"])
async def start(message) -> None:
    """
    Инициация команд lowprice", "highprice", "bestdeal
    :param message:
    :return:
    """
    await commands.low_high_price.start_request(message)


@bot.message_handler(commands=["history"])
async def show_history(message) -> None:
    """
    Показывает историю команд
    :param message:
    :return:
    """
    await commands.history.commands_history(message)


@bot.message_handler(func=lambda message: message.text.startswith('/'))
async def unknown_command(message):
    """
    Реакция бота на ввод неизвестной команды
    :param message:
    :return:
    """
    text = f"Неизвестная команда {message.text}\nДля просмотра доступных команд выберете /help"
    await bot.send_message(message.chat.id, text)


if __name__ == "__main__":
    asyncio.run(bot.infinity_polling())
