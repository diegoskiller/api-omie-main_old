from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo

class LoginForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    submit =  SubmitField("Login")


class RegisterForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired(), Length(min=3, max=20)])
    name = StringField("Nome", validators =[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired(), Length(min=6, max=16)])
    confirm_password=PasswordField("Confirme a senha", validators=[DataRequired(), EqualTo("password")])
    submit =  SubmitField("Cadastrar")
