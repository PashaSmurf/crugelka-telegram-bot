from aiogram.types import Message

from telegram_bot.resources.mysql.users import Users
from telegram_bot.resources.utils.images import Images

users = Users()
images = Images()


class Spam:
    @staticmethod
    async def send_spam(message: Message):
        active_users = users.select_active_users()
        if len(message.photo) == 0:
            for user in active_users:
                await message.bot.send_message(
                    user[0],
                    message.text.replace('/spam ', '')
                )
        else:
            for user in active_users:
                await message.bot.send_photo(
                    user[0],
                    photo=message.photo[-1].file_id,
                    caption=message.caption.replace('/spam ', '')
                )
