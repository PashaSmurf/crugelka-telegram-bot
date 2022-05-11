from mysql.connector import connect, errors

from telegram_bot.config.env_vars import MYSQL_HOST, MYSQL_LOGIN, \
    MYSQL_PASSWORD, MYSQL_DATABASE


class DBContainer:
    db_connection = None

    def insert(self, query: str):
        my_cursor = None
        try:
            my_cursor = self._get_connection().cursor()
            my_cursor.execute(query)
            self.db_connection.commit()
        except errors.IntegrityError as err:
            print(err)
        finally:
            my_cursor.close()

    def select(self, query: str) -> list:
        my_cursor = None
        try:
            my_cursor = self._get_connection().cursor()
            my_cursor.execute(query)
            cursor_list = my_cursor.fetchall()
            return cursor_list
        except errors.Error as err:
            print(err)
        finally:
            my_cursor.close()

    def multirow_insert(self, query: str, values: list):
        my_cursor = None
        try:
            my_cursor = self._get_connection().cursor()
            my_cursor.executemany(query, values)
            self.db_connection.commit()
        except errors.Error as err:
            print(err)
        finally:
            my_cursor.close()

    def _get_connection(self):
        if self.db_connection and self.db_connection.is_connected():
            return self.db_connection
        self.db_connection = self._connect()
        return self.db_connection

    @staticmethod
    def _connect():
        return connect(
                host=MYSQL_HOST,
                user=MYSQL_LOGIN,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
                port=3306
            )
