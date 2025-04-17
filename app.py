import base64
import os
import uuid
from datetime import datetime
from datetime import timedelta

from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from data import db_session
from data.article import Article
from data.article_image import ArticleImage
from data.users import User
from forms.create_article import CreateArticleForm
from forms.login import LoginForm
from forms.registration_forms import RegistrationForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '8200692859261968036'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["UPLOAD_FOLDER"] = 'static/img/uploads'

db_sess = None


@app.route('/')
def base_win():
    global db_sess, session
    user_id = session.get('id', None)
    if user_id:
        user = db_sess.query(User).filter(User.id == user_id).first()
        avatar_data = base64.b64encode(user.avatar).decode('utf-8')
        avatar_url = f"data:image/png;base64,{avatar_data}"
        return render_template(
            'base.html',
            user_authenticated=True,
            username=user.username,
            avatar_url=avatar_url,
            style=False
        )
    else:
        return render_template(
            'base.html',
            user_authenticated=False
        )


@app.route('/register', methods=['POST', 'GET'])
def register():
    user_id = session.get('id', None)
    if not user_id:
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
    else:
        return redirect(url_for('error'))


@app.route("/login", methods=["GET", "POST"])
def login():
    user_id = session.get('id', False)
    if not user_id:
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
                if not user:
                    flash("Пользователь с таким именем не найден", "error_username")
                else:
                    flash("Неверный пароль", "error_password")
        return render_template("login.html", form=form)
    else:
        return redirect(url_for('error'))


@app.route("/settings", methods=["GET", "POST"])
def settings():
    id = session.get('id', None)
    if id:
        user = db_sess.query(User).filter(User.id == id).first()
        avatar_data = base64.b64encode(user.avatar).decode('utf-8')
        avatar_url = f"data:image/png;base64,{avatar_data}"
        return render_template(
            "settings.html",
            user_authenticated=True,
            username=user.username,
            avatar_url=avatar_url
        )
    else:
        return redirect(url_for('error'))


@app.route("/create_article", methods=["GET", "POST"])
def create_article():
    user_id = session.get('id')
    if not user_id:
        return redirect(url_for('error'))

    form = CreateArticleForm()
    user = db_sess.query(User).filter(User.id == user_id).first()
    avatar_url = f"data:image/png;base64,{base64.b64encode(user.avatar).decode('utf-8')}"

    if request.method == "POST":
        is_fetch = request.accept_mimetypes['application/json'] or request.headers.get(
            'X-Requested-With') == 'XMLHttpRequest'

        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        font = request.form.get("font", "")
        comments_allowed = request.form.get("comments") == "1"
        image_files = request.files.getlist("images")

        errors = {}

        if not title:
            errors["title"] = "Заголовок не может быть пустым."
        if not content:
            errors["content"] = "Содержание не может быть пустым."
        if not font:
            errors["font"] = "Выберите шрифт."

        if errors:
            if is_fetch:
                return jsonify({"errors": errors}), 400
            else:
                return render_template("create_article.html", form=form, user_authenticated=True,
                                       username=user.username, avatar_url=avatar_url,
                                       style=False, title=title, content=content,
                                       font=font, comments_allowed=comments_allowed)

        new_article = Article(
            title=title,
            content=content,
            font=font,
            comments_allowed=comments_allowed,
            user_id=user_id,
            created_date=datetime.utcnow()
        )
        db_sess.add(new_article)
        db_sess.commit()

        for image in image_files:
            if image and image.filename and image.filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}:
                image_data = image.read()
                if image_data:
                    image_record = ArticleImage(
                        image_data=image_data,
                        article_id=new_article.id
                    )
                    db_sess.add(image_record)

        db_sess.commit()

        return redirect(url_for('base_win'))

    return render_template(
        "create_article.html",
        user_authenticated=True,
        username=user.username,
        avatar_url=avatar_url,
        style=False,
        form=form
    )


@app.route('/image/<int:image_id>')
def get_image(image_id):
    global db_sess
    image = db_sess.query(ArticleImage).get(image_id)
    if image:
        return app.response_class(image.image_data, mimetype='image/jpeg')  # Используем данные из БД
    else:
        abort(404)


@app.route("/profile")
def profile():
    id = session.get('id', None)
    if id:
        user = db_sess.query(User).filter(User.id == id).first()
        avatar_data = base64.b64encode(user.avatar).decode('utf-8')
        avatar_url = f"data:image/png;base64,{avatar_data}"
        return render_template(
            "profile.html",
            user_authenticated=True,
            username=user.username,
            avatar_url=avatar_url
        )
    else:
        return redirect(url_for('error'))


@app.route('/error')
def error():
    return render_template('error.html')


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
