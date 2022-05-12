from aiogram.types import Message

from telegram_bot.resources.mysql.users import Users

users = Users()


class Wish:

    @staticmethod
    async def send_wish(message: Message):
        admins = users.select_admins()
        if len(message.photo) == 0:
            for admin in admins:
                await message.bot.send_message(
                    admin[0],
                    f"@{message.from_user.username} - id: {message.from_user.id}. {message.text.replace('/wish ', '')}"
                )
        else:
            for admin in admins:
                await message.bot.send_photo(
                    admin[0],
                    photo=message.photo[-1].file_id,
                    caption=f"@{message.from_user.username} - id: {message.from_user.id}. {message.caption.replace('/wish ', '')}"
                )

