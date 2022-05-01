from aiogram.types import Message

from telegram_bot.resources.mysql.users import Users

users = Users()


class Spam:
    @staticmethod
    async def send_spam(message: Message):
        spam = message.text.replace('/spam ', '')
        active_users = users.select_active_users()
        for user in active_users:
            await message.bot.send_message(user[0], spam)
