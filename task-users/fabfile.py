# coding: utf-8
from __future__ import unicode_literals

from fabric.api import *


def setup_local():
    local('virtualenv env --no-site-packages', capture=False)
    local('env/bin/pip install -r requirements.txt', capture=False)


def update_local_env():
    local('env/bin/pip install -U -r requirements.txt', capture=False)


def make_prod_requirements():
    local(
        'env/bin/pip freeze -r requirements.txt > requirements_production.txt',
        capture=False,
    )
