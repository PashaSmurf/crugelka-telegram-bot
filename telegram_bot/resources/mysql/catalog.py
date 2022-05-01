import re

from telegram_bot.resources.mysql.connection import DBContainer


class Catalog:
    db_container = DBContainer()

    def get_fuzzy_vinyl(self, word: str, user_id: int):
        query = f'SELECT DISTINCT author, name, discogs, image, id, ' \
                f'IF(user_id = {user_id}, true, false) as in_bucket ' \
                f'FROM CATALOG LEFT OUTER JOIN BUCKET ON CATALOG.id = BUCKET.catalog_id ' \
                f'WHERE name LIKE \'%{word}%\' ' \
                f'OR author LIKE \'%{word}%\' OR category LIKE \'%{word}%\''

        cursor = self.db_container.select(query)
        return cursor.fetchall()

    def get_vinyl_by_number_and_length(self, word: str, number: int, user_id: int) -> tuple:
        try:
            results = self.get_fuzzy_vinyl(word, user_id)
            if len(results) > 10:
                return results, len(results)
            else:
                return results[number], len(results)
        except IndexError:
            return None, 0

    @staticmethod
    def get_info_from_caption(caption: str) -> tuple:
        return re.search('по: \'(.*?)\'', caption).group(1), \
               int(re.search('Стр: (.*?)\.', caption).group(1)), \
               int(re.search('Всего: (.*?)\.', caption).group(1))

    def add_vinyl_to_bucket(self, user_id, catalog_id):
        self.db_container.insert(f'INSERT INTO BUCKET (user_id, catalog_id) VALUES ({user_id}, {catalog_id});')

    def remove_vinyl_from_bucket(self, user_id, catalog_id):
        self.db_container.insert(f'DELETE FROM BUCKET WHERE user_id = {user_id} AND catalog_id = {catalog_id};')

    def select_vinyl_by_id(self, vinyl_id, user_id):
        query = f'SELECT DISTINCT author, name, discogs, image, id, ' \
                f'IF(user_id = {user_id}, true, false) as in_bucket ' \
                f'FROM CATALOG left outer join BUCKET on CATALOG.id = BUCKET.catalog_id ' \
                f'WHERE id = {vinyl_id}'
        cursor = self.db_container.select(query)
        return cursor.fetchall()[0]

    def get_bucket(self, user_id: int):
        query = \
            f'SELECT DISTINCT id, author, name ' \
            f'FROM CATALOG left outer join BUCKET ' \
            f'on CATALOG.id = BUCKET.catalog_id where user_id = {user_id};'

        cursor = self.db_container.select(query)
        return cursor.fetchall()

    def reset_bucket_by_user_id(self, user_id: int):
        self.db_container.insert(f'DELETE FROM BUCKET WHERE user_id = {user_id};')
