import pandas

from telegram_bot.config.env_vars import EXCEL_DOWNLOAD_PATH
from telegram_bot.resources.mysql.connection import DBContainer


class Migration:
    db_container = DBContainer()

    def excel_migration(self):
        values = []
        remove_query = 'DELETE FROM CATALOG;'
        query = 'INSERT INTO CATALOG (name, author, discogs, category, image) VALUES (%s, %s, %s, %s, %s);'
        sheet = pandas.read_excel(EXCEL_DOWNLOAD_PATH, sheet_name='vinyl')
        for row in sheet.iloc:
            values.append((row[0], row[1], row[2], row[4], row[3]))

        self.db_container.insert(remove_query)
        self.db_container.multirow_insert(query, values)
