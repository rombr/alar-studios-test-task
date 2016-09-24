# coding: utf-8
from __future__ import unicode_literals

import os
from logging.config import dictConfig as logging_dictConfig

from flask import Flask
from raven.contrib.flask import Sentry
from flask_bootstrap import Bootstrap


PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))


def prjpath(*args):
    return os.path.realpath(os.path.join(PROJECT_ROOT, *args))


try:
    from settings_production import STATIC_URL
except (ImportError):
    STATIC_URL = None


application = Flask(__name__, static_url_path=STATIC_URL)
# Load default config and override config from an environment variable
application.config.update(dict(
    DEBUG=False,
    LOGGER_NAME='mainapp',
    SECRET_KEY='8"6$RD=9!~3A"~}*8uRE*FP<X^~1^CGH66+Q;$e5u+?~"86+>@,',
    PASSWORD_SALT='Vmy~k^>eGF9f^=C(/!\'XRg)vT;,}i@_R1',
    SQLALCHEMY_DATABASE_URI=(
        'postgresql+psycopg2://dev:dev@localhost/alar_studios_testtask'
    ),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SENTRY_DSN='',
    PER_PAGE=5,
))
application.config.from_pyfile('settings_production.py', silent=True)
application.config.from_envvar('LOGIN_APP_SETTINGS', silent=True)

sentry = Sentry(application)
Bootstrap(application)


logging_dictConfig({
    'version': 1,
    'disable_existing_loggers': True,

    'formatters': {
        'console': {
            'format': (
                '[%(levelname)s][%(asctime)s] %(name)s %(filename)s:'
                '%(funcName)s:%(lineno)d | %(message)s'),
        },
    },

    'handlers': {
        'console': {
            'level': 'DEBUG' if application.config['DEBUG'] else 'ERROR',
            'class': 'logging.StreamHandler',
            # 'formatter': 'console',
        },
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': application.config['SENTRY_DSN'],
        },
    },

    'loggers': {
        '': {
            'handlers': ['console', 'sentry'],
            'level': 'WARNING',
            'propagate': False,
        },
        'mainapp': {
            'handlers': ['console', 'sentry'],
            'level': 'DEBUG' if application.config['DEBUG'] else 'WARNING',
            'propagate': False,
        },
    }
})

from . import views  # noqa
# pylama:ignore=W0611,D
