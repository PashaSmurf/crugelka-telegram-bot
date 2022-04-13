HELLO_WORDS = 'Привет!!!\nЯ - Бот-Crugelka и сейчас мы поможем выбрать Вам винил!'
UNAUTHORIZED_ERROR = 'Вы не Администратор!'
DOWNLOAD_LOADING = 'Подготовка файла к загрузке...'
DOWNLOAD_COMPLETED = 'Файл загружен! Запущен процесс обновления базы данных...'
MIGRATION_COMPLETED = 'Миграция окончена!'
IMAGE_DOWNLOAD_COMPLETED = 'Изображение загружено!'


def generate_users_string(cursor):
    message = 'Все пользователи Бота:\n'
    user_number = 1
    for row in cursor:
        message += f'{user_number}. @{row[1]}\n'
        user_number += 1

    return message
