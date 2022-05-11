import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ContentTypes, Message

from telegram_bot.config.constant_strings import HELLO_WORDS, generate_users_string, \
    DOWNLOAD_LOADING, DOWNLOAD_COMPLETED, MIGRATION_COMPLETED, EXTRACT_STARTED, \
    ZIP_DOWNLOAD_COMPLETED
from telegram_bot.config.env_vars import TELEGRAM_API_TOKEN, EXCEL_DOWNLOAD_PATH, ZIP_DOWNLOAD_PATH
from telegram_bot.decorators.decorators import is_admin
from telegram_bot.resources.excel.migration import Migration
from telegram_bot.resources.mysql.catalog import Catalog

from telegram_bot.resources.mysql.users import Users
from telegram_bot.resources.services.bucket import Bucket
from telegram_bot.resources.services.catalog_table import CatalogTable
from telegram_bot.resources.services.slider import Slider
from telegram_bot.resources.services.spam import Spam
from telegram_bot.resources.utils.images import Images

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher(bot)
users = Users()
migration = Migration()
catalog = Catalog()
bucket = Bucket()
spam = Spam()
catalog_table = CatalogTable()
images = Images()
slider = Slider()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    users.insert_user(message.chat.id, message.chat.username, message.chat.full_name)
    await message.reply(HELLO_WORDS)


@dp.message_handler(commands=['bucket'])
async def show_user_bucket(message: types.Message):
    await bucket.show_bucket(message)


@dp.message_handler(commands=['spam'])
async def send_spam(message: types.Message):
    await spam.send_spam(message)


@dp.message_handler(commands=['users'])
@is_admin
async def get_users(message: types.Message):
    await message.reply(generate_users_string(users.select_users()))


@dp.message_handler(content_types=ContentTypes.DOCUMENT)
@is_admin
async def file_handle(message: Message):
    await message.reply(text=DOWNLOAD_LOADING)
    if message.document.mime_subtype == 'zip':
        await message.document.download(destination_file=ZIP_DOWNLOAD_PATH)
        await message.reply(text=EXTRACT_STARTED)
        images.extract_zip()
        await message.reply(text=ZIP_DOWNLOAD_COMPLETED)
    else:
        await message.document.download(destination_file=EXCEL_DOWNLOAD_PATH)
        await message.reply(text=DOWNLOAD_COMPLETED)
        migration.excel_migration()
        await message.reply(text=MIGRATION_COMPLETED)


@dp.message_handler(content_types=ContentTypes.PHOTO)
@is_admin
async def image_handle(message: Message):
    await images.store_image(message)


@dp.message_handler()
async def get_fuzzy_vinyl(message: types.Message):
    await catalog_table.show_table(message)


@dp.callback_query_handler(lambda c: 'list' in c.data)
async def process_callback_table_button(callback_query: types.CallbackQuery):
    await slider.open_short_slider_from_table(callback_query)


@dp.callback_query_handler(lambda c: 'table_return_button' in c.data)
async def process_callback_table_return_button(callback_query: types.CallbackQuery):
    await catalog_table.edit_table(callback_query, None)


@dp.callback_query_handler(lambda c: 'table_add_button' in c.data)
async def process_callback_table_add_button(callback_query: types.CallbackQuery):
    await slider.edit_short_slider(callback_query)


@dp.callback_query_handler(lambda c: 'table_remove_button' in c.data)
async def process_callback_table_remove_button(callback_query: types.CallbackQuery):
    await slider.edit_short_slider(callback_query)


@dp.callback_query_handler(lambda c: 'table_next_button' in c.data)
async def process_callback_table_next_button(callback_query: types.CallbackQuery):
    await catalog_table.edit_table(callback_query, 'next')


@dp.callback_query_handler(lambda c: 'table_back_button' in c.data)
async def process_callback_table_back_button(callback_query: types.CallbackQuery):
    await catalog_table.edit_table(callback_query, 'back')


@dp.callback_query_handler(lambda c: 'bucket_next_button' in c.data)
async def process_callback_bucket_next_button(callback_query: types.CallbackQuery):
    await bucket.edit_bucket(callback_query, 'next')


@dp.callback_query_handler(lambda c: 'bucket_back_button' in c.data)
async def process_callback_bucket_back_button(callback_query: types.CallbackQuery):
    await bucket.edit_bucket(callback_query, 'back')


@dp.callback_query_handler(lambda c: 'remove_bucket_button' in c.data)
async def process_callback_remove_bucket_button(callback_query: types.CallbackQuery):
    await bucket.remove_item_from_bucket(callback_query)


@dp.callback_query_handler(lambda c: c.data == 'bucket_send_button')
async def process_callback_send_bucket_button(callback_query: types.CallbackQuery):
    await bucket.send_bucket_to_admin(callback_query)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
