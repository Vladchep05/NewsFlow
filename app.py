from datetime import timedelta

from flask import Flask, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash

from data import db_session
from data.users import User
from forms.login import LoginForm
from forms.registration_forms import RegistrationForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '8200692859261968036'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)


@app.route('/')
@app.route('/home')
def base_win():
    return render_template('base.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    usr_data = [session.get('id', None), session.get('email', None), session.get('password', None)]
    form = RegistrationForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        # Получаем данные регестрации
        username = form.username.data
        email = form.email.data
        password = form.password.data
        country = form.country.data

        check_username = db_sess.query(User).filter(User.username == username).first()
        if check_username:
            flash('Пользователь с таким именем уже существует!', category='error_username')
            return redirect(url_for('register'))

        check_email = db_sess.query(User).filter(User.email == email).first()
        if check_email:
            flash('Пользователь с таким email уже существует!', category='error_email')
            return redirect(url_for('register'))

        # Хешируем пароль
        hashed_password = generate_password_hash(password)

        # Создаём нового пользователя
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            country=country
        )

        # Добавляем в базу данных
        db_sess.add(new_user)
        db_sess.commit()

        session['id'] = new_user.id
        session['email'] = new_user.email
        session['password'] = new_user.hashed_password

        return redirect('/')

    return render_template('registration.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # логика входа (проверка email/пароля, сессии и т.п.)
        flash('Успешный вход!', 'success')
        return redirect(url_for('profile'))  # или куда нужно
    return render_template('login.html', form=form)


def main():
    db_session.global_init("db/data.db")
    app.run(host='0.0.0.0', port=8080, debug=True)


if __name__ == '__main__':
    main()
