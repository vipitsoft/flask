# coding:utf-8
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import Required, Length


class NameForm(Form):
    name = StringField("What is your name?", validators=[Required()])
    submit = SubmitField('提交')


# 用户资料编辑器
class EditProfileForm(Form):
    name = StringField('姓名', validators=[Length(0, 64)])
    location = StringField('地址', validators=[Length(0, 64)])
    about_me = TextAreaField('自我介绍')
    submit = SubmitField('提交')