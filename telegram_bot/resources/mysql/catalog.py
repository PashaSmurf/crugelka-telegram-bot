import re

from telegram_bot.resources.mysql.connection import DBContainer


class Catalog:
    db_container = DBContainer()

    def get_fuzzy_vinyl(self, word: str):
        query = f'SELECT DISTINCT author, name, discogs, image ' \
                f'FROM CATALOG WHERE name LIKE \'%{word}%\' ' \
                f'OR author LIKE \'%{word}%\' OR category LIKE \'%{word}%\''

        cursor = self.db_container.select(query)
        return cursor.fetchall()

    def get_vinyl_by_number_and_length(self, word: str, number: int) -> tuple:
        try:
            results = self.get_fuzzy_vinyl(word)
            return results[number], len(results)
        except IndexError:
            return None, 0

    @staticmethod
    def get_info_from_caption(caption: str) -> tuple:
        return re.search('по: \'(.*?)\'', caption).group(1), \
               int(re.search('\n(.*?)\.', caption).group(1)), \
               int(re.search('Всего: (.*?)\n', caption).group(1))
