from itertools import islice
from typing import Optional

from aiogram import types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from telegram_bot.config.env_vars import TABLE_SIZE
from telegram_bot.resources.mysql.catalog import Catalog
from telegram_bot.resources.services.slider import Slider
from telegram_bot.resources.utils.images import Images

catalog = Catalog()
images = Images()
slider = Slider()


class CatalogTable:
    def show_table(self, message: Message):
        vinyl = catalog.get_vinyl_by_number_and_length(message.text, message.from_user.id)
        if len(vinyl) == 0:
            return message.bot.send_message(message.chat.id, 'Нет результатов')
        else:
            return message.bot.send_photo(
                chat_id=message.chat.id,
                photo=images.get_image('table-preview'),
                caption=self.get_table(len(vinyl), 1, message.text),
                reply_markup=self.get_table_markup(vinyl, 0, message.text)
            )

    @staticmethod
    def get_table(length: int, number: int, word: str):
        return f'Результаты по: \'{word}\'. Всего: {length}. Стр: {number}.\n'

    def get_table_markup(self, results: list, number: int, word: str):
        inline_keyboard = InlineKeyboardMarkup()
        for row in islice(results, number * TABLE_SIZE, number * TABLE_SIZE + TABLE_SIZE):
            inline_button = InlineKeyboardButton(f'{row[0]} - {row[1]}', callback_data=f'list|{row[4]}|{number}|{word}')
            inline_keyboard.add(inline_button)
        return self.get_table_buttons(inline_keyboard, number, len(results), word)

    def get_table_buttons(self, inline_keyboard, number: int, length: int, word: str):
        inline_table_back_button = InlineKeyboardButton('Back', callback_data=f'table_back_button|{number}|{word}')
        inline_table_next_button = InlineKeyboardButton('Next', callback_data=f'table_next_button|{number}|{word}')
        if number == 0 and length > TABLE_SIZE:
            return inline_keyboard.add(inline_table_next_button)
        elif number == 0 and length <= TABLE_SIZE:
            return inline_keyboard
        elif number != 0 and length > TABLE_SIZE * number:
            return inline_keyboard.add(inline_table_back_button, inline_table_next_button)
        else:
            return inline_keyboard.add(inline_table_back_button)

    def edit_table(self, callback_query: types.CallbackQuery, action: Optional[str]):
        split = callback_query.data.split('|')
        split_number = int(split[1])
        number = split_number + 1 if action == 'next' else split_number - 1 if action == 'back' else split_number
        message = split[2]
        vinyl = catalog.get_vinyl_by_number_and_length(message, callback_query.from_user.id)
        return callback_query.bot.edit_message_media(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            media=types.InputMedia(
                type='photo',
                caption=self.get_table(len(vinyl), number + 1, message),
                media=images.get_image('table-preview')),
            reply_markup=self.get_table_markup(vinyl, number, message)
        )

