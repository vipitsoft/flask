# coding:utf-8
from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, login_required, logout_user, current_user
from . import auth
from forms import LoginForm, RegistrationForm
from ..models import User
from .. import db
from ..email import send_email


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'错误的用户名或密码！')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'登出成功！')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
        except:
            db.session.rollback()
            raise
        finally:
            db.session.close()

        token = user.generate_confirmation_token()
        send_email(user.email, u'确认账号', 'auth/email/confirm', user=user, token=token)
        flash(u'确认邮件已经发送到您的邮箱，请注意查收！')
        return redirect(url_for('auth.login',user=user))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('auth.login'))
    if current_user.confirm(token):
        flash(u'您已经确认了账户，谢谢！')
        return redirect(url_for('auth.login'))
    else:
        flash(u'确认链接无效或已过期！')
    return redirect(url_for('auth.login'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated and \
        not current_user.confirmed \
        and request.endpoint[:5] != 'auth.' \
        and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, u'确认账号！', user=current_user, token=token)
    flash(u'已经发送了一封新邮件到您的账户，请确认！')
    return redirect(url_for('main.index'))


# 更新已登录用户的访问时间
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))