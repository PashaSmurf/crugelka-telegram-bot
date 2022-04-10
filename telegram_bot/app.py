import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ContentTypes, Message

from telegram_bot.config.constant_strings import HELLO_WORDS, generate_users_string, UNAUTHORIZED_ERROR, \
    DOWNLOAD_LOADING, DOWNLOAD_COMPLETED, MIGRATION_COMPLETED, IMAGE_DOWNLOAD_COMPLETED
from telegram_bot.config.env_vars import TELEGRAM_API_TOKEN, EXCEL_DOWNLOAD_PATH, IMAGE_DOWNLOAD_PATH
from telegram_bot.resources.excel.migration import Migration

from telegram_bot.resources.mysql.users import Users

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher(bot)
users = Users()
migration = Migration()


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


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
