import os

# telegram bit API key
TELEGRAM_API_TOKEN = os.environ.get('TELEGRAM_API_TOKEN')

# mysql creds
MYSQL_HOST = os.environ.get('MYSQL_HOST')
MYSQL_LOGIN = os.environ.get('MYSQL_LOGIN')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')

# file path
EXCEL_DOWNLOAD_PATH = os.environ.get('EXCEL_DOWNLOAD_PATH')
ZIP_DOWNLOAD_PATH = os.environ.get('ZIP_DOWNLOAD_PATH')
IMAGE_DOWNLOAD_PATH = os.environ.get('IMAGE_DOWNLOAD_PATH')

# table configs
TABLE_SIZE = int(os.environ.get('TABLE_SIZE', 5))
