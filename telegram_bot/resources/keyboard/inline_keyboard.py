from itertools import islice

from aiogram import types, Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from telegram_bot.config.env_vars import IMAGE_DOWNLOAD_PATH, TABLE_SIZE
from telegram_bot.resources.mysql.catalog import Catalog

catalog = Catalog()


class InlineKeyBoard:
    inline_back_button = InlineKeyboardButton('Back', callback_data='back_button')
    inline_next_button = InlineKeyboardButton('Next', callback_data='next_button')
    inline_add_button = InlineKeyboardButton('Добавить для обсуждения', callback_data='add_button')
    inline_cancel_button = InlineKeyboardButton('Убрать из обсуждения', callback_data='cancel_button')
    inline_return_button = InlineKeyboardButton('Обратно к таблице', callback_data='return_button')
    inline_table_back_button = InlineKeyboardButton('Back', callback_data='table_back_button')
    inline_table_next_button = InlineKeyboardButton('Next', callback_data='table_next_button')

    inline_kb_back_and_next_add = InlineKeyboardMarkup().add(inline_back_button, inline_next_button).add(inline_add_button)
    inline_kb_back_only_add = InlineKeyboardMarkup().add(inline_back_button).add(inline_add_button)
    inline_kb_next_only_add = InlineKeyboardMarkup().add(inline_next_button).add(inline_add_button)
    inline_kb_add_only_add = InlineKeyboardMarkup().add(inline_add_button)

    inline_kb_back_and_next_cancel = InlineKeyboardMarkup().add(inline_back_button, inline_next_button).add(inline_cancel_button)
    inline_kb_back_only_cancel = InlineKeyboardMarkup().add(inline_back_button).add(inline_cancel_button)
    inline_kb_next_only_cancel = InlineKeyboardMarkup().add(inline_next_button).add(inline_cancel_button)
    inline_kb_add_only_cancel = InlineKeyboardMarkup().add(inline_cancel_button)

    inline_kb_return_cancel = InlineKeyboardMarkup().add(inline_cancel_button).add(inline_return_button)
    inline_kb_return_add = InlineKeyboardMarkup().add(inline_add_button).add(inline_return_button)

    inline_kb_table_next_back = InlineKeyboardMarkup().add(inline_table_back_button).add(inline_table_next_button)
    inline_kb_table_back = InlineKeyboardMarkup().add(inline_table_back_button)
    inline_kb_table_next = InlineKeyboardMarkup().add(inline_table_next_button)

    @staticmethod
    def get_caption(number: int, word: str, length: int, author: str, name: str, discogs: str) -> str:
        return f'Результаты по: \'{word}\'. Всего: {length}. Стр: {number}.\n{author} - {name}\nDiscogs - {discogs}'

    @staticmethod
    def get_table(length: int, number: int, word: str):
        return f'Результаты по: \'{word}\'. Всего: {length}. Стр: {number}.\n'

    @staticmethod
    def get_image(name: str):
        return open(f'{IMAGE_DOWNLOAD_PATH}{name}.png', 'rb')

    def get_table_markup(self, results: list, number: int):
        inline_keyboard = InlineKeyboardMarkup()
        for row in islice(results, number * TABLE_SIZE, number * TABLE_SIZE + TABLE_SIZE):
            inline_button = InlineKeyboardButton(f'{row[0]} - {row[1]}', callback_data=f'list-{row[4]}')
            inline_keyboard.add(inline_button)
        return self.get_table_buttons(inline_keyboard, number + 1, len(results))

    def initial_slider(self, number: int, bot, message: str, user_id: int, chat_id: int):
        vinyl, length = catalog.get_vinyl_by_number_and_length(message, number, user_id)
        if length == 0:
            return bot.send_message(chat_id, 'Нет результатов')
        if not isinstance(vinyl, list):
            return bot.send_photo(chat_id,
                                  caption=self.get_caption(1, message, length, vinyl[0], vinyl[1], vinyl[2]),
                                  photo=self.get_image(vinyl[3]),
                                  reply_markup=self.get_markup(1, length, vinyl[5]))
        else:
            return bot.send_photo(
                chat_id=chat_id,
                photo=self.get_image('table-preview'),
                caption=self.get_table(len(vinyl), number + 1, message),
                reply_markup=self.get_table_markup(vinyl, number)
            )

    def edit_slider(self, number: int, bot, message: str, message_id: int, chat_id: int, user_id: int):
        vinyl, length = catalog.get_vinyl_by_number_and_length(message, number, user_id)
        return bot.edit_message_media(
            chat_id=chat_id,
            message_id=message_id,
            media=types.InputMedia(
                type='photo',
                caption=self.get_caption(number + 1, message, length, vinyl[0], vinyl[1], vinyl[2]),
                media=self.get_image(vinyl[3])),
            reply_markup=self.get_markup(number + 1, length, vinyl[5]))

    def get_markup(self, number, length, is_in_bucket):
        if number == 1 and number == length:
            return self.inline_kb_add_only_cancel if is_in_bucket else self.inline_kb_add_only_add
        elif number == 1 and number < length:
            return self.inline_kb_next_only_cancel if is_in_bucket else self.inline_kb_next_only_add
        elif number != 1 and number < length:
            return self.inline_kb_back_and_next_cancel if is_in_bucket else self.inline_kb_back_and_next_add
        else:
            return self.inline_kb_back_only_cancel if is_in_bucket else self.inline_kb_back_only_add

    def open_slider_from_table(self, word, number, length, vinyl_id: int, bot: Bot, chat_id: int, message_id: int, user_id: int):
        vinyl = catalog.select_vinyl_by_id(vinyl_id, user_id)
        return bot.edit_message_media(
            chat_id=chat_id,
            message_id=message_id,
            media=types.InputMedia(
                type='photo',
                caption=self.get_caption(number, word, length, vinyl[0], vinyl[1], vinyl[2]),
                media=self.get_image(vinyl[3])),
            reply_markup=self.inline_kb_return_cancel if vinyl[5] else self.inline_kb_return_add)

    def get_table_buttons(self, inline_keyboard, number: int, length: int):
        if number == 1 and length > TABLE_SIZE:
            return inline_keyboard.add(self.inline_table_next_button)
        elif number == 1 and length <= TABLE_SIZE:
            return inline_keyboard
        elif number != 1 and length > TABLE_SIZE * number:
            return inline_keyboard.add(self.inline_table_back_button, self.inline_table_next_button)
        else:
            return inline_keyboard.add(self.inline_table_back_button)

    def edit_table(self, number: int, bot, message: str, message_id: int, chat_id: int, user_id: int):
        vinyl, length = catalog.get_vinyl_by_number_and_length(message, number, user_id)
        return bot.edit_message_media(
            chat_id=chat_id,
            message_id=message_id,
            media=types.InputMedia(
                type='photo',
                caption=self.get_table(len(vinyl), number + 1, message),
                media=self.get_image('table-preview')),
            reply_markup=self.get_table_markup(vinyl, number)
        )

    @staticmethod
    def get_slider_caption_only(author, name, discogs):
        return f'{author} - {name}\nDiscogs - {discogs}'
