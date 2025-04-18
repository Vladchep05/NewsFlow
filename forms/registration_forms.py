import json
import os
import re

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms import EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError


def load_countries():
    json_path = os.path.join('static', 'data', 'countries.json')
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    return [(c['code'], c['name']) for c in data]


# Кастомный валидатор для проверки сложности пароля
def password_complexity(form, field):
    password = field.data
    if not re.search(r'[A-ZА-Я]', password):  # Проверка на заглавную букву
        raise ValidationError('Пароль должен содержать хотя бы одну заглавную букву (например, A, B или А, Б).')
    if not re.search(r'[a-zа-я]', password):  # Проверка на строчную букву
        raise ValidationError('Пароль должен содержать хотя бы одну заглавную букву (например, a, b или а, б).')
    if not re.search(r'[0-9]', password):  # Проверка на цифру
        raise ValidationError('Пароль должен содержать хотя бы одну цифру (например, 1, 2 или 9).')
    if not re.search(r'[\W_]', password):  # Проверка на спецсимвол
        raise ValidationError('Пароль должен содержать хотя бы один специальный символ (например, !, @, # или _).')
    if len(password) < 8:  # Проверка на минимальную длину
        raise ValidationError('Пароль должен содержать не менее 8 символов.')


class RegistrationForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired(), Length(min=4, max=22)])
    email = EmailField('Email', validators=[DataRequired(message="Поле email обязательно."),
                                            Email(message="Некорректный адрес электронной почты.")])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6),
                                                   password_complexity])
    confirm_password = PasswordField('Подтвердите пароль', validators=[
        DataRequired(),
        EqualTo('password', message='Пароли должны совпадать')
    ])
    country = SelectField('Страна', choices=load_countries(), validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
