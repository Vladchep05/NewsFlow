from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp


class ConfirmationAuthorization(FlaskForm):
    code = StringField(
        'Код подтверждения',
        validators=[
            DataRequired(message='Пожалуйста, введите код.'),
            Length(min=6, max=6, message='Код должен содержать 6 символов.'),
            Regexp(r'^\d{6}$', message='Код должен содержать только цифры.')
        ]
    )
    submit = SubmitField('Подтвердить')
