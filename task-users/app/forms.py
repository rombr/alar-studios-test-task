# coding: utf-8
from __future__ import unicode_literals

from collections import OrderedDict

from flask.ext.wtf import Form
from wtforms_alchemy import model_form_factory
from wtforms import (
    StringField, PasswordField, SubmitField,
)
from wtforms.validators import (
    DataRequired, Length, Email, EqualTo,
)

from .models import User, db


BaseModelForm = model_form_factory(Form, strip_string_fields=True)


class OrderFormMixin(object):
    '''
    To apply add to Meta 'order' iterable
    '''
    def __init__(self, *args, **kwargs):
        super(OrderFormMixin, self).__init__(*args, **kwargs)

        field_order = getattr(self.meta, 'order', [])
        if field_order:
            visited = []
            new_fields = OrderedDict()

            for field_name in field_order:
                if field_name in self._fields:
                    new_fields[field_name] = self._fields[field_name]
                    visited.append(field_name)

            for field_name in self._fields:
                if field_name in visited:
                    continue
                new_fields[field_name] = self._fields[field_name]

            self._fields = new_fields


class ModelForm(OrderFormMixin, BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


class LoginForm(Form):
    '''
    Login
    '''
    email = StringField(
        'E-mail',
        validators=[
            DataRequired(),
            Length(max=120),
            Email(),
        ],
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(max=128),
        ],
    )
    submit = SubmitField('Login')


class AddUserForm(ModelForm):
    '''
    For add user
    '''
    new_password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=6, max=128),
            EqualTo(
                'repeat_new_password',
                message='Passwords must be equal.',
            ),
        ],
    )
    repeat_new_password = PasswordField(
        'Retype password',
        validators=[
            DataRequired(),
            Length(min=6, max=128),
        ],
    )
    submit = SubmitField('Add')

    class Meta:
        model = User
        only = ('email', 'role', )
        order = (
            'email', 'role',
            'new_password', 'repeat_new_password',
            'submit',
        )


class ChangeUserPasswordForm(ModelForm):
    '''
    Change user password
    '''
    new_password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=6, max=128),
            EqualTo(
                'repeat_new_password',
                message='Passwords must be equal.',
            ),
        ],
    )
    repeat_new_password = PasswordField(
        'Retype password',
        validators=[
            DataRequired(),
            Length(min=6, max=128),
        ],
    )
    submit = SubmitField('Change')


class EditUserForm(ModelForm):
    '''
    For change user
    '''
    submit = SubmitField('Save')

    class Meta:
        model = User
        only = ('email', 'role', )
        order = ('email', 'role', 'submit', )
