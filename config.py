import json
import os


BOT_TOKEN = os.environ.get("BOT_TOKEN")
AIO_TOKEN = os.environ.get("AIO_TOKEN")
admins = json.loads(os.environ['ADMINS'])

