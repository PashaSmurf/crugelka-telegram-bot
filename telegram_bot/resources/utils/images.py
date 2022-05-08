import zipfile

from aiogram.types import Message

from telegram_bot.config.constant_strings import IMAGE_DOWNLOAD_COMPLETED
from telegram_bot.config.env_vars import IMAGE_DOWNLOAD_PATH, ZIP_DOWNLOAD_PATH


class Images:
    @staticmethod
    def get_image(name: str):
        try:
            return open(f"{IMAGE_DOWNLOAD_PATH}{name if name else 'default'}.png", 'rb')
        except FileNotFoundError:
            return open(f"{IMAGE_DOWNLOAD_PATH}default.png", 'rb')

    @staticmethod
    async def store_image(message: Message):
        await message.photo[-1].download(destination_file=IMAGE_DOWNLOAD_PATH + message.html_text + '.png')
        await message.reply(text=IMAGE_DOWNLOAD_COMPLETED)

    @staticmethod
    def extract_zip():
        with zipfile.ZipFile(ZIP_DOWNLOAD_PATH, 'r') as zip_ref:
            zip_ref.extractall(IMAGE_DOWNLOAD_PATH)
