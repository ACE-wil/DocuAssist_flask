from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, Email

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

class QuestionForm(FlaskForm):
    content = StringField('题目内容', validators=[DataRequired()])
    answer = StringField('答案', validators=[DataRequired()])
    difficulty = IntegerField('难度', validators=[DataRequired()])
    submit = SubmitField('添加题目')

class UserForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('添加用户')

class SettingsForm(FlaskForm):
    site_name = StringField('网站名称', validators=[DataRequired()])
    maintenance_mode = BooleanField('维护模式')
    submit = SubmitField('保存设置')

class ProfileForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('新密码')
    submit = SubmitField('更新资料')
