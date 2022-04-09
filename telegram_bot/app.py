import logging
from aiogram import Bot, Dispatcher, executor, types

from telegram_bot.config.constant_strings import HELLO_WORDS
from telegram_bot.config.env_vars import TELEGRAM_API_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply(HELLO_WORDS)


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
