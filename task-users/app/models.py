# coding: utf-8
from __future__ import unicode_literals

from hashlib import md5

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import ChoiceType
from wtforms.validators import Email

from . import application
from const import USER_ROLES, ROLE_READONLY, ROLE_FULL


db = SQLAlchemy(application)


class User(db.Model):
    '''
    Users
    '''
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(
        db.String(120), unique=True, nullable=False,
        info={
            'label': 'E-mail',
            'validators': Email(),
        },
    )
    password = db.Column(
        db.String(32), nullable=False,
        info={
            'label': 'Password',
            'trim': False,
        },
    )
    role = db.Column(
        ChoiceType(USER_ROLES),
        nullable=False, default=ROLE_READONLY,
        info={
            'label': 'Role',
        },
    )

    def __init__(self, email, password, role):
        self.email = email
        self.role = role
        self.password = self.encrypt(password)

    @classmethod
    def encrypt(cls, password):
        '''
        Encrypt password for storing
        '''
        salt = current_app.config['PASSWORD_SALT']
        return md5(unicode(password) + salt).hexdigest()

    @property
    def can_edit(self):
        return self.role == ROLE_FULL

    def __repr__(self):
        return '<User %r>' % self.email


@application.before_first_request
def init_db():
    current_app.logger.debug('Init db')
    if not db.engine.dialect.has_table(db.engine.connect(), 'users'):
        db.create_all()

    if not User.query.count():
        seed_user = User('admin@example.com', 'password', ROLE_FULL)
        db.session.add(seed_user)
        db.session.commit()
