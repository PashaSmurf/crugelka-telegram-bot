import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ContentTypes, Message, InlineKeyboardButton, InlineKeyboardMarkup

from telegram_bot.config.constant_strings import HELLO_WORDS, generate_users_string, UNAUTHORIZED_ERROR, \
    DOWNLOAD_LOADING, DOWNLOAD_COMPLETED, MIGRATION_COMPLETED, IMAGE_DOWNLOAD_COMPLETED
from telegram_bot.config.env_vars import TELEGRAM_API_TOKEN, EXCEL_DOWNLOAD_PATH, IMAGE_DOWNLOAD_PATH
from telegram_bot.resources.excel.migration import Migration
from telegram_bot.resources.mysql.catalog import Catalog

from telegram_bot.resources.mysql.users import Users

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher(bot)
users = Users()
migration = Migration()
catalog = Catalog()
inline_back_button = InlineKeyboardButton('Back', callback_data='back_button')
inline_next_button = InlineKeyboardButton('Next', callback_data='next_button')
inline_add_button = InlineKeyboardButton('Добавить для обсуждения', callback_data='add_button')
inline_kb_back_and_next = InlineKeyboardMarkup().add(inline_back_button, inline_next_button).add(inline_add_button)
inline_kb_back_only = InlineKeyboardMarkup().add(inline_back_button).add(inline_add_button)
inline_kb_next_only = InlineKeyboardMarkup().add(inline_next_button).add(inline_add_button)
inline_kb_add_only = InlineKeyboardMarkup().add(inline_add_button)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
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
    vinyl, length = catalog.get_vinyl_by_number_and_length(message.text, 0)
    if length > 0:
        await bot.send_photo(message.chat.id,
                             caption=f'Результат поиска по: \'{message.text}\'. Всего: {length}\n1. {vinyl[0]} - {vinyl[1]}\nDiscogs - {vinyl[2]}',
                             photo=open(f'{IMAGE_DOWNLOAD_PATH}{vinyl[3]}.png', 'rb'),
                             reply_markup=inline_kb_next_only if length > 1 else inline_kb_add_only)
    else:
        await bot.send_message(message.chat.id, 'Нет результатов')


@dp.callback_query_handler(lambda c: c.data == 'next_button')
async def process_callback_next_button(callback_query: types.CallbackQuery):
    word, number, length = catalog.get_info_from_caption(callback_query.message.caption)
    vinyl, length = catalog.get_vinyl_by_number_and_length(word, number)
    await bot.edit_message_media(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        media=types.InputMedia(
            type='photo',
            caption=f'Результат поиска по: \'{word}\'. Всего: {length}\n{number + 1}. {vinyl[0]} - {vinyl[1]}\nDiscogs - {vinyl[2]}',
            media=open(f'{IMAGE_DOWNLOAD_PATH}{vinyl[3]}.png', 'rb')),
        reply_markup=inline_kb_back_only if number + 1 == length else inline_kb_back_and_next)


@dp.callback_query_handler(lambda c: c.data == 'back_button')
async def process_callback_back_button(callback_query: types.CallbackQuery):
    word, number, length = catalog.get_info_from_caption(callback_query.message.caption)
    vinyl, length = catalog.get_vinyl_by_number_and_length(word, number - 2)
    await bot.edit_message_media(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        media=types.InputMedia(
            type='photo',
            caption=f'Результат поиска по: \'{word}\'. Всего: {length}\n{number - 1}. {vinyl[0]} - {vinyl[1]}\nDiscogs - {vinyl[2]}',
            media=open(f'{IMAGE_DOWNLOAD_PATH}{vinyl[3]}.png', 'rb')),
        reply_markup=inline_kb_next_only if number - 1 == 1 else inline_kb_back_and_next)


@dp.callback_query_handler(lambda c: c.data == 'add_button')
async def process_callback_add_button(callback_query: types.CallbackQuery):
    word, number, length = catalog.get_info_from_caption(callback_query.message.caption)
    vinyl, length = catalog.get_vinyl_by_number_and_length(word, number)
    await bot.send_message(555352073, "test message")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
