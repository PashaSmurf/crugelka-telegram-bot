import pandas

from telegram_bot.config.env_vars import EXCEL_DOWNLOAD_PATH
from telegram_bot.resources.mysql.connection import DBContainer


class Migration:
    db_container = DBContainer()

    def excel_migration(self):
        values = []

        remove_bucket = 'DELETE FROM BUCKET;'
        remove_catalog = 'DELETE FROM CATALOG;'
        reset_auto = 'ALTER TABLE CATALOG AUTO_INCREMENT = 1;'
        query = 'INSERT INTO CATALOG (name, author, discogs, category, image, in_stock) VALUES (%s, %s, %s, %s, %s, %s);'
        sheet = pandas.read_excel(EXCEL_DOWNLOAD_PATH, sheet_name='vinyl')
        for row in sheet.iloc:
            values.append((row[0], row[1], '' if str(row[2]) == 'nan' else row[2], row[4], row[3], int(row[5])))

        self.db_container.insert(remove_bucket)
        self.db_container.insert(remove_catalog)
        self.db_container.insert(reset_auto)
        self.db_container.multirow_insert(query, values)
