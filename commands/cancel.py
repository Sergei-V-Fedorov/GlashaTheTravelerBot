"""Реализация команды cancel"""
from bot_init import bot


@bot.message_handler(state="*", commands=["cancel"])
async def cancel_state(message):
    """
    Прерывает диалог поиска
    """
    current_state = await bot.get_state(message.from_user.id, message.chat.id)
    if current_state is None:
        await bot.send_message(message.chat.id, "Поиск ещё не производится. Введите команду")
    else:
        await bot.send_message(message.chat.id, "Поиск был отменён. Введите команду")
        await bot.delete_state(message.from_user.id, message.chat.id)
