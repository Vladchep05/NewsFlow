from datetime import timedelta

from flask import Flask, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import base64

from data import db_session
from data.users import User
from forms.login import LoginForm
from forms.registration_forms import RegistrationForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '8200692859261968036'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db_sess = None


@app.route('/')
def base_win():
    global db_sess
    id = session.get('id', None)
    if id:
        user = db_sess.query(User).filter(User.id == id).first()
        avatar_data = base64.b64encode(user.avatar).decode('utf-8')
        avatar_url = f"data:image/png;base64,{avatar_data}"
        return render_template(
            'base.html',
            user_authenticated=True,
            username=user.username,
            avatar_url=avatar_url
        )
    else:
        return render_template(
            'base.html',
            user_authenticated=False
        )


@app.route('/register', methods=['POST', 'GET'])
def register():
    global db_sess
    form = RegistrationForm()
    if form.validate_on_submit():
        # Получаем данные регестрации
        username = form.username.data
        email = form.email.data
        password = form.password.data
        country = form.country.data

        check_username = db_sess.query(User).filter(User.username == username).first()
        if check_username:
            flash('Пользователь с таким именем уже существует!', category='error_username')
            return render_template('registration.html', form=form)

        check_email = db_sess.query(User).filter(User.email == email).first()
        if check_email:
            flash('Пользователь с таким email уже существует!', category='error_email')
            return render_template('registration.html', form=form)

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

        return redirect('/')

    return render_template('registration.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    global db_sess
    form = LoginForm()
    if form.validate_on_submit():
        name = form.username.data
        password = form.password.data
        user = db_sess.query(User).filter(User.username == name).first()
        if user and check_password_hash(user.hashed_password, password):
            session['id'] = user.id
            remember = form.remember.data
            if remember:
                global app
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=365)
            else:
                session.permanent = False
            return redirect('/')
        else:
            flash("Неверное имя пользователя или пароль", "danger")
    return render_template("login.html", form=form)


@app.route('/check', methods=['POST', 'GET'])
def regist():
    form = RegistrationForm()
    print(session.get('id'))
    return render_template('registration.html', form=form)


@app.route('/exit', methods=['GET'])
def exit():
    session.pop('id')
    return render_template(
        'base.html',
        user_authenticated=False
    )


def main():
    global db_sess
    db_session.global_init("db/data.db")
    db_sess = db_session.create_session()
    app.run(host='0.0.0.0', port=8080, debug=True)


if __name__ == '__main__':
    main()
