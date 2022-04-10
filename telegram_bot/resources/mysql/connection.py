from mysql.connector import Error, connect, cursor, errors

from telegram_bot.config.env_vars import MYSQL_HOST, MYSQL_LOGIN, \
    MYSQL_PASSWORD, MYSQL_DATABASE


class DBContainer:
    db_connection = None

    def insert(self, query: str):
        try:
            my_cursor = self._get_connection().cursor()
            my_cursor.execute(query)
            self.db_connection.commit()
        except errors.IntegrityError as err:
            print(err)

    def select(self, query: str) -> cursor:
        try:
            my_cursor = self._get_connection().cursor()
            my_cursor.execute(query)
            return my_cursor
        except errors.Error as err:
            print(err)

    def multirow_insert(self, query: str, values: list):
        try:
            my_cursor = self._get_connection().cursor()
            my_cursor.executemany(query, values)
            self.db_connection.commit()
        except errors.Error as err:
            print(err)

    def _get_connection(self):
        if not self.db_connection:
            self.db_connection = self._connect()
        return self.db_connection

    @staticmethod
    def _connect():
        return connect(
                host=MYSQL_HOST,
                user=MYSQL_LOGIN,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE
            )
