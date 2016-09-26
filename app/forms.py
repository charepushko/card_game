from flask_wtf import Form
from wtforms import TextField, BooleanField, PasswordField
from wtforms.validators import Required

class LoginForm(Form):
    openid = TextField('openid', validators=[Required()])
    password = PasswordField('password', validators=[Required()])
    remember_me = BooleanField('remember_me', default=True)

class SignUpForm(Form):
    login = TextField('login', validators=[Required()])
    email = TextField('email', validators=[Required()])
    password = PasswordField('password', validators=[Required()])
