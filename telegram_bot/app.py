import logging
import re

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ContentTypes, Message

from telegram_bot.config.constant_strings import HELLO_WORDS, generate_users_string, UNAUTHORIZED_ERROR, \
    DOWNLOAD_LOADING, DOWNLOAD_COMPLETED, MIGRATION_COMPLETED, IMAGE_DOWNLOAD_COMPLETED
from telegram_bot.config.env_vars import TELEGRAM_API_TOKEN, EXCEL_DOWNLOAD_PATH, IMAGE_DOWNLOAD_PATH
from telegram_bot.resources.excel.migration import Migration
from telegram_bot.resources.keyboard.inline_keyboard import InlineKeyBoard
from telegram_bot.resources.mysql.catalog import Catalog

from telegram_bot.resources.mysql.users import Users

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher(bot)
users = Users()
migration = Migration()
catalog = Catalog()
inline_keyboard = InlineKeyBoard()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    users.insert_user(message.chat.id, message.chat.username)
    await message.reply(HELLO_WORDS)


@dp.message_handler(commands=['help'])
async def get_help(message: types.Message):
    users.insert_user(message.chat.id, message.chat.username)
    await message.reply(HELLO_WORDS)


@dp.message_handler(commands=['users'])
async def get_users(message: types.Message):
    if users.is_admin(message.chat.id):
        await message.reply(generate_users_string(users.select_users()))
    else:
        await message.reply(UNAUTHORIZED_ERROR)


@dp.message_handler(content_types=ContentTypes.DOCUMENT)
async def file_handle(message: Message):
    if users.is_admin(message.chat.id):
        await message.reply(text=DOWNLOAD_LOADING)
        await message.document.download(destination_file=EXCEL_DOWNLOAD_PATH)
        await message.reply(text=DOWNLOAD_COMPLETED)
        migration.excel_migration()
        await message.reply(text=MIGRATION_COMPLETED)
    else:
        await message.reply(UNAUTHORIZED_ERROR)


@dp.message_handler(content_types=ContentTypes.PHOTO)
async def image_handle(message: Message):
    if users.is_admin(message.chat.id):
        await message.photo[-1].download(destination_file=IMAGE_DOWNLOAD_PATH + message.html_text + '.png')
        await message.reply(text=IMAGE_DOWNLOAD_COMPLETED)
    else:
        await message.reply(UNAUTHORIZED_ERROR)


@dp.message_handler()
async def get_fuzzy_vinyl(message: types.Message):
    await inline_keyboard.initial_slider(0, bot, message.text, message.from_user.id, message.chat.id)


@dp.callback_query_handler(lambda c: c.data == 'next_button')
async def process_callback_next_button(callback_query: types.CallbackQuery):
    word, number, length = catalog.get_info_from_caption(callback_query.message.caption)
    await inline_keyboard.edit_slider(number, bot, word, callback_query.message.message_id, callback_query.message.chat.id, callback_query.from_user.id)


@dp.callback_query_handler(lambda c: c.data == 'back_button')
async def process_callback_back_button(callback_query: types.CallbackQuery):
    word, number, length = catalog.get_info_from_caption(callback_query.message.caption)
    await inline_keyboard.edit_slider(number - 2, bot, word, callback_query.message.message_id, callback_query.message.chat.id, callback_query.from_user.id)


@dp.callback_query_handler(lambda c: c.data == 'add_button')
async def process_callback_add_button(callback_query: types.CallbackQuery):
    word, number, length = catalog.get_info_from_caption(callback_query.message.caption)
    vinyl, length = catalog.get_vinyl_by_number_and_length(word, number - 1, callback_query.from_user.id)
    catalog.add_vinyl_to_bucket(callback_query.from_user.id, vinyl[4])
    await inline_keyboard.edit_slider(number - 1, bot, word, callback_query.message.message_id, callback_query.message.chat.id, callback_query.from_user.id)


@dp.callback_query_handler(lambda c: c.data == 'cancel_button')
async def process_callback_cancel_button(callback_query: types.CallbackQuery):
    word, number, length = catalog.get_info_from_caption(callback_query.message.caption)
    vinyl, length = catalog.get_vinyl_by_number_and_length(word, number - 1, callback_query.from_user.id)
    catalog.remove_vinyl_from_bucket(callback_query.from_user.id, vinyl[4])
    await inline_keyboard.edit_slider(number - 1, bot, word, callback_query.message.message_id, callback_query.message.chat.id, callback_query.from_user.id)


@dp.callback_query_handler(lambda c: c.data == 'back_button')
async def process_callback_back_button(callback_query: types.CallbackQuery):
    word, number, length = catalog.get_info_from_caption(callback_query.message.caption)
    await inline_keyboard.edit_slider(number - 2, bot, word, callback_query.message.message_id, callback_query.message.chat.id, callback_query.from_user.id)


@dp.callback_query_handler(lambda c: 'list' in c.data)
async def process_callback_table_button(callback_query: types.CallbackQuery):
    word, number, length = catalog.get_info_from_caption(callback_query.message.caption)
    await inline_keyboard.open_slider_from_table(word, number, length, int(callback_query.data.split('list-')[1]), bot, callback_query.message.chat.id, callback_query.message.message_id, callback_query.from_user.id)


@dp.callback_query_handler(lambda c: c.data == 'table_next_button')
async def process_callback_table_next_button(callback_query: types.CallbackQuery):
    word, number, length = catalog.get_info_from_caption(callback_query.message.caption)
    await inline_keyboard.edit_table(number, bot, word, callback_query.message.message_id, callback_query.message.chat.id, callback_query.from_user.id)


@dp.callback_query_handler(lambda c: c.data == 'table_back_button')
async def process_callback_table_back_button(callback_query: types.CallbackQuery):
    word, number, length = catalog.get_info_from_caption(callback_query.message.caption)
    await inline_keyboard.edit_table(number - 2, bot, word, callback_query.message.message_id, callback_query.message.chat.id, callback_query.from_user.id)


@dp.callback_query_handler(lambda c: c.data == 'return_button')
async def process_callback_return_button(callback_query: types.CallbackQuery):
    word, number, length = catalog.get_info_from_caption(callback_query.message.caption)
    await inline_keyboard.edit_table(number - 1, bot, word, callback_query.message.message_id, callback_query.message.chat.id, callback_query.from_user.id)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
