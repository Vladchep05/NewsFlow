from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, Optional


class CreateArticleForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(message="Заголовок обязателен"),
                                                 Length(min=5, message="Заголовок должен быть не менее 5 символов")])
    content = TextAreaField('Содержание', validators=[DataRequired(message="Содержание обязательно")])
    font = SelectField('Шрифт', choices=[('Arial', 'Arial'), ('Courier New', 'Courier New'), ('Verdana', 'Verdana'),
                                         ('Times New Roman', 'Times New Roman'), ('Poppins', 'Poppins')],
                       validators=[DataRequired(message="Пожалуйста, выберите шрифт")])
    comments_allowed = BooleanField('Разрешить комментарии')
