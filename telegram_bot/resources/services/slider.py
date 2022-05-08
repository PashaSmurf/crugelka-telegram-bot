from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from telegram_bot.resources.mysql.catalog import Catalog
from telegram_bot.resources.utils.images import Images

catalog = Catalog()
images = Images()


class Slider:
    def open_short_slider_from_table(self, callback_query: types.CallbackQuery):
        split = callback_query.data.split('|')
        vinyl_id = int(split[1])
        word = split[3]
        number = int(split[2])
        vinyl = catalog.select_vinyl_by_id(vinyl_id, callback_query.from_user.id)
        return callback_query.bot.edit_message_media(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            media=types.InputMedia(
                type='photo',
                caption=self.get_short_slider_caption(vinyl[0], vinyl[1], vinyl[2]),
                media=images.get_image(vinyl[3])),
            reply_markup=self.get_short_slider_buttons(vinyl_id, word, number, vinyl[5]))

    @staticmethod
    def get_short_slider_caption(author: str, name: str, discogs: str):
        return f'{author} - {name}\nDiscogs: {discogs}'

    @staticmethod
    def get_short_slider_buttons(vinyl_id: int, word: str, number: int, in_bucket: bool):
        inline_add_button = InlineKeyboardButton('Добавить для обсуждения', callback_data=f'table_add_button|{vinyl_id}|{number}|{word}')
        inline_cancel_button = InlineKeyboardButton('Убрать из обсуждения', callback_data=f'table_remove_button|{vinyl_id}|{number}|{word}')
        inline_return_button = InlineKeyboardButton('Обратно к таблице', callback_data=f'table_return_button|{number}|{word}')
        inline_kb_return_cancel = InlineKeyboardMarkup().add(inline_cancel_button).add(inline_return_button)
        inline_kb_return_add = InlineKeyboardMarkup().add(inline_add_button).add(inline_return_button)
        return inline_kb_return_cancel if in_bucket else inline_kb_return_add

    def edit_short_slider(self, callback_query: types.CallbackQuery):
        split = callback_query.data.split('|')
        vinyl_id = int(split[1])
        number = int(split[2])
        word = split[3]
        if split[0] == 'table_add_button':
            catalog.add_vinyl_to_bucket(callback_query.from_user.id, vinyl_id)
        else:
            catalog.remove_vinyl_from_bucket(callback_query.from_user.id, vinyl_id)
        vinyl = catalog.select_vinyl_by_id(vinyl_id, callback_query.from_user.id)
        return callback_query.bot.edit_message_media(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            media=types.InputMedia(
                type='photo',
                caption=self.get_short_slider_caption(vinyl[0], vinyl[1], vinyl[2]),
                media=images.get_image(vinyl[3])),
            reply_markup=self.get_short_slider_buttons(vinyl_id, word, number, vinyl[5]))
