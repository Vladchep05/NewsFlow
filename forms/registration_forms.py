import json
import os

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms import EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo


def load_countries():
    json_path = os.path.join('static', 'data', 'countries.json')
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    return [(c['code'], c['name']) for c in data]


class RegistrationForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[
        DataRequired(),
        EqualTo('password', message='Пароли должны совпадать')
    ])
    country = SelectField('Страна', choices=load_countries(), validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
