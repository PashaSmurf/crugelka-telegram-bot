HELLO_WORDS = 'Привет!!!\nЯ - Бот-Crugelka и сейчас мы поможем выбрать Вам винил!'
UNAUTHORIZED_ERROR = 'Вы не Администратор!'
DOWNLOAD_LOADING = 'Подготовка файла к загрузке...'
DOWNLOAD_COMPLETED = 'Файл загружен! Запущен процесс обновления базы данных...'
EXTRACT_STARTED = 'Файл загружен! Запущен процесс извлечения...'
MIGRATION_COMPLETED = 'Миграция окончена!'
IMAGE_DOWNLOAD_COMPLETED = 'Изображение загружено!'
ZIP_DOWNLOAD_COMPLETED = 'Архив загружен!'


def generate_users_string(users: list):
    message = 'Все пользователи Бота:\n'
    user_number = 1
    for user in users:
        message += f'{user_number}. @{user[1]}\n'
        user_number += 1

    return message
