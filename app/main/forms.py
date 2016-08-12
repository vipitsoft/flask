# coding:utf-8
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from  flask.ext.pagedown.fields import PageDownField
from wtforms.validators import Required, Length, Email, Regexp, ValidationError
from ..models import Role, User


class NameForm(Form):
    name = StringField("What is your name?", validators=[Required()])
    submit = SubmitField('提交')


# 用户资料编辑器
class EditProfileForm(Form):
    name = StringField(u'姓名', validators=[Length(0, 64)])
    location = StringField(u'地址', validators=[Length(0, 64)])
    about_me = TextAreaField(u'自我介绍')
    submit = SubmitField(u'提交')


# 管理员资料编辑器
class EditProfileAdminForm(Form):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                                '用户名必须是唯一的，'
                                                                                '数字，字母或下划线')])
    confirmed = BooleanField(u'确认')
    role = SelectField(u'角色', coerce=int)
    name = StringField(u'姓名', validators=[Length(0, 64)])
    localtion = StringField(u'位置', validators=[Length(0, 64)])
    about_me = TextAreaField(u'介绍')
    submit = SubmitField(u'提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已被注册！')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已使用！')


class PostForm(Form):
    body = PageDownField(u"在想什么？", validators=[Required()])
    submit = SubmitField(u'提交')


class CommentForm(Form):
    body = StringField('', validators=[Required()])
    submit = SubmitField(u'提交')