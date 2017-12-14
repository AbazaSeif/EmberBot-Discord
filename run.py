#!/usr/bin/env pypy3
from gevent import monkey
monkey.patch_all()

import argparse
parser = argparse.ArgumentParser(description="Start or test Ember Tipbot.")
parser.add_argument('-m', '--mode', default="prod", choices=("test", "local", "dev", "prod", "db_create", "db_destroy"), help="Start mode.")
args = parser.parse_args()

import os
import sys
import os.path
import traceback
from base import config
from gevent.wsgi import WSGIServer
from gevent import socket
from werkzeug.serving import run_with_reloader

from psycopg2cffi import compat
compat.register()
from psycogreen.gevent import patch_psycopg
patch_psycopg()

from flask_sqlalchemy import SQLAlchemy

import discord
from discord.ext import commands

def main():
    from base.bot import bot_run
    from base.models import Model
    from base.models import create_all

    if args.mode == "test":
        import unittest
        import test
        testsuite = unittest.TestLoader().discover('.')
        testrunner = unittest.TextTestRunner(verbosity=2)
        ret = not testrunner.run(testsuite).wasSuccessful()
        sys.exit(ret)
    if args.mode == "db_create":
        import subprocess
        subprocess.call(["sudo -u postgres 'createuser -h 127.0.0.1 -U postgres -D -R -S -P %s'" % (config.DB["user"],)], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.call(["sudo -u postgres 'createdb -h 127.0.0.1 -U postgres -O %s %s'" % (config.DB["user"], config.DB["name"],)], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        create_all()
    elif args.mode == "db_destroy":
        import subprocess
        subprocess.call(["sudo -u postgres 'dropdb %s'" % (config.DB["name"],)], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.call(["sudo -u postgres 'dropuser %s'" % (config.DB["user"],)], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        print("Running Ember Tipbot Server")
        bot_run()

if __name__ == '__main__':
    main()