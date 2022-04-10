import logging
from aiogram import Bot, Dispatcher, executor, types

from telegram_bot.config.constant_strings import HELLO_WORDS, generate_users_string, UNAUTHORIZED_ERROR
from telegram_bot.config.env_vars import TELEGRAM_API_TOKEN
from telegram_bot.resources.mysql.users import Users

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher(bot)
users = Users()


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


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
