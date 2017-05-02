#coding:utf-8

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, SubmitField,PasswordField
from wtforms.validators import DataRequired,Length, Email, EqualTo


class CommonForm(FlaskForm):
    types = SelectField(u'博文分类', coerce=int, validators=[DataRequired()])
    source = SelectField(u'博文来源', coerce=int, validators=[DataRequired()])


class SubMitArticlesForm(CommonForm):
    title = StringField(u'标题', validators=[DataRequired(), Length(1, 64)])
    content = TextAreaField(u'博文内容',validators=[DataRequired()])
    summary = TextAreaField(u'博文摘要', validators=[DataRequired()])




