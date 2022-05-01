from aiogram.types import Message

from telegram_bot.config.constant_strings import UNAUTHORIZED_ERROR
from telegram_bot.resources.mysql.users import Users

USERS = Users()


def is_admin(func):
    async def wrapper(*args):
        message: Message = args[0]
        if USERS.is_admin(message.from_user.id):
            return await func(message)
        else:
            await message.reply(UNAUTHORIZED_ERROR)
    return wrapper
