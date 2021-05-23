import os

AUTO_UPDATE_TIME = 20

SERVER_INVITE = "https://discord.gg/dATz7vwbN2"
BOT_INVITE = "https://discord.com/api/oauth2/authorize?client_id=796548435825393674&permissions=2550656064&scope=bot"
GITHUB_LINK = "https://github.com/Proyecto-Nutria/otter-buddy"

OTTER_ADMIN = os.environ.get('OTTER_ADMIN', 'Admin')
OTTER_MODERATOR = os.environ.get('OTTER_MODERATOR', 'Moderator')

DATA_DIR = 'data'
LOGS_DIR = 'logs'

ASSETS_DIR = os.path.join(DATA_DIR, 'assets')
MISC_DIR = os.path.join(DATA_DIR, 'misc')
TEMP_DIR = os.path.join(DATA_DIR, 'temp')

LOG_FILE_PATH = os.path.join(LOGS_DIR, 'otter-buddy.log')

ALL_DIRS = (attrib_value for attrib_name, attrib_value in list(globals().items())
            if attrib_name.endswith('DIR'))

PREFIX = "&"
BRAND_COLOR = 0x0099A2
