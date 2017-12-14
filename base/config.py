#!/usr/bin/env python
import os
from datetime import timedelta

basedir = os.environ.get("BASE_DIR")

DEBUG = False

SERVER_NAME = 'www.0xify.com/tipbot/'

LOG_FILE = 'tipbot.log'

# administrator list
ADMINS = ['_@0xify.com']
ADMIN_KEY = os.environ.get("ADMIN_KEY")
TEST_KEY = os.environ.get("TEST_KEY")

UPLOAD_FOLDER = '/home/andrewbc/tipbot/uploads'

LOGGING = {
    "print_level": 3,
    "file": "log.txt",
    "file_level": 3
}

SECRET_KEY = os.environ.get("SECRET_KEY", None)
DB = {
    'driver': os.environ.get("DB_DRIVER", None),
    'user': os.environ.get("DB_USER", None),
    'pass': os.environ.get("DB_PASS", None),
    'host': os.environ.get("DB_HOST", None),
    'port': os.environ.get("DB_PORT", None),
    'name': os.environ.get("DB_NAME", None),
}
if not DB['user'] and not DB['pass'] and not DB['host'] and not DB['port']:
    print("SQLite Mode")
    SQLALCHEMY_DATABASE_URI = u"%s:///%s" % (DB['driver'], os.path.join(basedir, DB['name']))
else:
    print("PostgreSQL Mode")
    SQLALCHEMY_DATABASE_URI = u"%s://%s:%s@%s:%s/%s" % (DB['driver'], DB['user'], DB['pass'], DB['host'], DB['port'], DB['name'])
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'migrations')
SQLALCHEMY_TRACK_MODIFICATIONS = False
CSRF_ENABLED = True

DISCORD_TOKEN = "MzcxMTQxNTE4MjE3NDQ1Mzc4.DQoXSA.lZUyuxKMQm6y8-h9OutospCmhmg"
DISCORD_CLIENT_ID = "371141518217445378"
DISCORD_OWNERS = ("241772266285826049",)
DISCORD_PREFIX = "!"
DISCORD_DESC = "Ember Tipbot"
RPC = {
    "host": "127.0.0.1",
    "port": "10022",
    "user": "abc",
    "pass": "ItIsaVerryGoodTimeToPanic&&&^&^&^****"
}

NET_TAX = 10000 #in bignum form, so this is 0.00010000
PERSONAL_TAX = 3 # parts out of 100.
TAX_COLLECTOR = "eAJ7m2G84gJgaA27Fuvy1sqZhoW8tHmFeN"
