# coding: utf-8
from __future__ import unicode_literals

from functools import wraps

from flask import (
    render_template, redirect, url_for, g, abort,
    request, flash, current_app, session,
)

from . import application
from .models import User, db
from .forms import LoginForm, AddUserForm, ChangeUserPasswordForm, EditUserForm


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not get_current_user():
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def edit_perm_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if user and not user.can_edit:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    if not hasattr(g, 'user'):
        if 'user_id' in session:
            g.user = User.query.filter_by(id=session['user_id']).first()
            current_app.logger.debug('Current user %r', g.user)
            if not g.user:
                del session['user_id']
        else:
            g.user = None

    return g.user


@application.route('/')
def index():
    '''
    Main page
    '''
    return redirect(url_for('users'))


@application.route('/login/', methods=['POST', 'GET'])
def login():
    next_page = request.args.get('next', None)
    # TODO: # Security check

    if not next_page:
        next_page = url_for('index')

    if get_current_user():
        return redirect(next_page)

    login_form = LoginForm(request.form)
    if request.method == 'POST' and login_form.validate():

        user = User.query.filter_by(
            email=login_form.email.data,
            password=User.encrypt(login_form.password.data),
        ).first()

        if user is None:
            flash('Invalid user or password!', 'danger')
        else:
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(next_page)

    return render_template(
        'login.html',
        login_form=login_form,
    )


@application.route('/logout/')
def logout():
    '''
    Logout
    '''
    try:
        del session['user_id']
    except KeyError:
        pass
    return redirect(url_for('login'))


@application.route('/users/')
@login_required
def users():
    '''
    Users list
    '''
    return render_template(
        'users.html',
        users=User.query.order_by('id').paginate(
            per_page=current_app.config['PER_PAGE'],
            error_out=False,
        )
    )


@application.route('/users/add/', methods=['POST', 'GET'])
@edit_perm_required
@login_required
def add_user():
    '''
    Add new user
    '''
    form = AddUserForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(
            form.email.data,
            form.new_password.data,
            form.role.data,
        )
        db.session.add(user)
        db.session.commit()

        flash('User added successful!', 'success')
        return redirect(url_for('users'))

    return render_template(
        'add_user.html',
        form=form,
    )


@application.route('/users/<int:pk>/change/password/', methods=['POST', 'GET'])
@edit_perm_required
@login_required
def change_user_password(pk):
    '''
    Change user password
    '''
    user = User.query.filter_by(id=pk).first_or_404()

    form = ChangeUserPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        user.password = User.encrypt(form.new_password.data)
        db.session.add(user)
        db.session.commit()

        flash('Password changed successful!', 'success')
        return redirect(url_for('users'))

    return render_template(
        'change_user_password.html',
        form=form,
        user=user,
    )


@application.route('/users/<int:pk>/', methods=['POST', 'GET'])
@login_required
def edit_user(pk):
    '''
    Change or delete user
    '''
    user = User.query.filter_by(id=pk).first_or_404()

    if not g.user.can_edit:
        form = None
        if request.method == 'POST':
            abort(403)
    else:
        # Remove
        if request.method == 'POST' and 'delete' in request.form:
            db.session.delete(user)
            db.session.commit()

            flash('User deleted successful!', 'success')
            return redirect(url_for('users'))

        # Edit
        form = EditUserForm(request.form, obj=user)
        if request.method == 'POST' and form.validate():
            form.populate_obj(user)
            db.session.add(user)
            db.session.commit()

            flash('User changed successful!', 'success')
            return redirect(url_for('users'))

    return render_template(
        'edit_user.html',
        form=form,
        user=user,
    )
