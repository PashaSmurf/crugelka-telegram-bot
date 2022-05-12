from itertools import islice

from aiogram import types
from aiogram.types import InlineKeyboardButton, Message, InlineKeyboardMarkup

from telegram_bot.config.env_vars import TABLE_SIZE
from telegram_bot.resources.mysql.catalog import Catalog
from telegram_bot.resources.mysql.users import Users

catalog = Catalog()
users = Users()


class Bucket:

    inline_bucket_send_button = InlineKeyboardButton('Отправить', callback_data='bucket_send_button')

    def show_bucket(self, message: Message):
        bucket = catalog.get_bucket(message.from_user.id)
        if len(bucket) == 0:
            return message.bot.send_message(
                chat_id=message.chat.id,
                text='У Вас пока нет предпочтений'
            )
        return message.bot.send_message(
            chat_id=message.chat.id,
            text=self.get_bucket_caption(0, len(bucket)),
            reply_markup=self.get_bucket_markup(0, bucket)
        )

    def edit_bucket(self, callback_query: types.CallbackQuery, action: str):
        bucket = catalog.get_bucket(callback_query.from_user.id)
        number = int(callback_query.data.split('button|')[1])
        return callback_query.bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text=self.get_bucket_caption(number + 1 if action == 'next' else number - 1, len(bucket)),
            reply_markup=self.get_bucket_markup(number + 1 if action == 'next' else number - 1, bucket)
        )

    def get_bucket_markup(self, number: int, bucket: list):
        inline_keyboard = InlineKeyboardMarkup()
        for row in islice(bucket, number * TABLE_SIZE, number * TABLE_SIZE + TABLE_SIZE):
            inline_button = InlineKeyboardButton(f'Убрать {row[1]} - {row[2]}', callback_data=f'remove_bucket_button|{row[0]}')
            inline_keyboard.add(inline_button)
        return self.get_bucket_buttons(inline_keyboard, number, len(bucket))

    @staticmethod
    def get_bucket_caption(number: int, length: int):
        from_number = number * TABLE_SIZE + 1
        to_number = length if number * TABLE_SIZE + TABLE_SIZE > length else number * TABLE_SIZE + TABLE_SIZE
        return f'Ваши предпочтения: {from_number} - {to_number} из {length}'

    def get_bucket_buttons(self, inline_keyboard, number: int, length: int):
        inline_bucket_back_button = InlineKeyboardButton('Back', callback_data=f'bucket_back_button|{number}')
        inline_bucket_next_button = InlineKeyboardButton('Next', callback_data=f'bucket_next_button|{number}')
        if number == 0 and length > TABLE_SIZE:
            inline_keyboard.add(inline_bucket_next_button)
        elif number == 0 and number < length:
            pass
        elif number != 0 and length > TABLE_SIZE * (number + 1):
            inline_keyboard.add(inline_bucket_back_button, inline_bucket_next_button)
        else:
            inline_keyboard.add(inline_bucket_back_button)

        return inline_keyboard.add(self.inline_bucket_send_button)

    def remove_item_from_bucket(self, callback_query: types.CallbackQuery):
        vinyl_id = int(callback_query.data.split('button|')[1])
        catalog.remove_vinyl_from_bucket(callback_query.from_user.id, vinyl_id)
        bucket = catalog.get_bucket(callback_query.from_user.id)
        if len(bucket) == 0:
            return callback_query.bot.edit_message_text(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                text='У Вас нет предпочтений',
            )
        return callback_query.bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text=self.get_bucket_caption(0, len(bucket)),
            reply_markup=self.get_bucket_markup(0, bucket)
        )

    async def send_bucket_to_admin(self, callback_query: types.CallbackQuery):
        bucket = catalog.get_bucket(callback_query.from_user.id)
        catalog.reset_bucket_by_user_id(callback_query.from_user.id)
        admins = users.select_admins()
        for admin in admins:
            await callback_query.bot.send_message(
                admin[0],
                self.get_all_bucket(bucket, str(callback_query.from_user.username))
            )
        await callback_query.bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text='Вы отправили свои предпочтения. С Вами свяжутся в ближайшее время',
            reply_markup=None
        )

    @staticmethod
    def get_all_bucket(bucket: list, username: str) -> str:
        result = f'Пользователь - @{username}\nПожелания:\n'
        for item in bucket:
            result += f'{item[1]} - {item[2]}\n'
        return result
