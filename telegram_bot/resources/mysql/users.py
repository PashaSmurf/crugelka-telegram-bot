from telegram_bot.resources.mysql.connection import DBContainer


class Users:
    db_container = DBContainer()

    def insert_user(self, user_id: int, username: str):
        self.db_container.insert(f'INSERT INTO USERS (id, username, role) VALUES ({user_id}, \'{username}\', {0})')

    def select_users(self):
        return self.db_container.select('SELECT * FROM USERS').fetchall()

    def is_admin(self, user_id: int):
        user = self.db_container.select(f'SELECT ROLE FROM USERS WHERE ID = {user_id}')
        for row in user:
            return row[0]

    def select_active_users(self):
        return self.db_container.select('SELECT id FROM USERS WHERE ban = 0').fetchall()
