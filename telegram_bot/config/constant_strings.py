HELLO_WORDS = 'Привет!!!\nЯ - Бот-Crugelka и сейчас мы поможем выбрать Вам винил!'
UNAUTHORIZED_ERROR = 'Вы не Администратор!'


def generate_users_string(cursor):
    message = 'Все пользователи Бота:\n'
    user_number = 1
    for row in cursor:
        message += f'{user_number}. @{row[1]}\n'
        user_number += 1

    return message
