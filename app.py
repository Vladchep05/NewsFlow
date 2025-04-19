from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from random import randint
from smtplib import SMTP
import threading
import hashlib
import base64
import json
import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

from data import db_session
from data.article import Article
from data.article_image import ArticleImage
from data.users import User
from forms.create_article import CreateArticleForm
from forms.form_confirmation import ConfirmationAuthorization
from forms.login import LoginForm
from forms.registration_forms import RegistrationForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '8200692859261968036'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["UPLOAD_FOLDER"] = 'static/img/uploads'

db_sess = None


@app.route('/home')
@app.route('/')
def base_win():
    global db_sess, session
    user_id = session.get('id', None)
    articles = db_sess.query(Article).order_by(Article.created_date.desc()).all()

    # Дополнительная обработка для каждой статьи
    for article in articles:
        author = article.user
        if author and author.avatar:
            avatar_data = base64.b64encode(author.avatar).decode('utf-8')
            article.author = {
                'username': author.username,
                'avatar_url': f"data:image/png;base64,{avatar_data}"
            }
        else:
            article.author = {
                'username': 'Аноним',
                'avatar_url': url_for('static', filename='img/avatar/default.jpg')
            }

        # Первая картинка статьи, если есть
        if article.images:
            img_data = base64.b64encode(article.images[0].image_data).decode('utf-8')
            article.image_url = f"data:image/png;base64,{img_data}"
        else:
            article.image_url = None

    if user_id:
        user = db_sess.query(User).filter(User.id == user_id).first()
        avatar_url = None
        if user.avatar:
            avatar_data = base64.b64encode(user.avatar).decode('utf-8')
            avatar_url = f"data:image/png;base64,{avatar_data}"

        load_dotenv()
        key = os.getenv("KEY")
        cipher = Fernet(key)

        user_id = cipher.encrypt(str(user_id).encode()).decode()

        return render_template(
            'base.html',
            user_authenticated=True,
            username=user.username,
            avatar_url=avatar_url,
            style=False,
            user_id=user_id
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

            session['username'] = username
            session['email'] = email
            session['hashed_password'] = hashed_password
            session['country'] = country
            session['remaining_time'] = 300

            # Генерация 6-значного кода
            code = str(randint(100000, 999999))
            session['code'] = hashlib.sha256(code.encode()).hexdigest()

            thread = threading.Thread(target=sending_code, args=('register', email, code))
            thread.start()

            return redirect(url_for('confirmation', typ='register'))

        return render_template('registration.html', form=form)
    else:
        return redirect(url_for('error'))


@app.route("/login", methods=["GET", "POST"])
def login():
    user_id = session.get('id', False)
    if not user_id:
        form = LoginForm()
        if form.validate_on_submit():
            global db_sess
            username = form.username.data
            password = form.password.data
            user = db_sess.query(User).filter(User.username == username).first()
            if user and check_password_hash(user.hashed_password, password):
                remember = form.remember.data

                session['username'] = username
                session['email'] = user.email
                session['remember'] = remember
                session['remaining_time'] = 300

                # Генерация 6-значного кода
                code = str(randint(100000, 999999))
                session['code'] = hashlib.sha256(code.encode()).hexdigest()

                thread = threading.Thread(target=sending_code, args=('login', user.email, code))
                thread.start()

                return redirect(url_for('confirmation', typ='login'))
            else:
                if not user:
                    flash("Пользователь с таким именем не найден", "error_username")
                else:
                    flash("Неверный пароль", "error_password")
        return render_template("login.html", form=form)
    else:
        return redirect(url_for('error'))


def sending_code(typ, email, code):
    load_dotenv()

    email_sender = os.getenv("EMAIL_SENDER")
    email_password = os.getenv("EMAIL_PASSWORD")

    with open("templates/confirmation_mail.html", "r", encoding="utf-8") as file:
        html_template = file.read()

    if typ == 'register':
        message = 'Вы запрашивали код подтверждения регистрации в системе NewsFlow.'
        subject = "Подтверждение регистрации — NewsFlow"
    else:
        message = 'Вы запрашивали код подтверждения для входа в систему NewsFlow.'
        subject = "Подтверждение входа — NewsFlow"

    html = html_template.format(message=message, code=code)

    # Создание письма
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"NewsFlow <{email_sender}>"
    msg["To"] = email

    # Прикрепляем HTML как MIMEText
    msg.attach(MIMEText(html, "html"))

    # Отправка
    with SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(email_sender, email_password)
        server.send_message(msg)


@app.route("/confirmation/<typ>", methods=["GET", "POST"])
def confirmation(typ):
    global session
    user_id = session.get('id', None)

    # Проверяем, если user_id в сессии, иначе показываем ошибку
    if not user_id:
        form = ConfirmationAuthorization()

        # Понимание оставшегося времени в сессии (если оно есть)
        remaining_time = session.get('remaining_time', 300)  # Если нет, то по умолчанию 5 минут (300 секунд)

        if request.method == "POST":
            if form.validate_on_submit():
                entered_code = form.code.data
                code = session.get('code', None)

                if hashlib.sha256(entered_code.encode()).hexdigest() == code:
                    # Удаляем код из сессии, если он правильный
                    session.pop('code', None)

                    # Логика регистрации или логина
                    if typ == 'register':
                        username = session.pop('username', None)
                        email = session.pop('email', None)
                        hashed_password = session.pop('hashed_password', None)
                        country = session.pop('country', None)

                        # Создаём нового пользователя
                        new_user = User(
                            username=username,
                            email=email,
                            hashed_password=hashed_password,
                            country=country
                        )
                        db_sess.add(new_user)
                        db_sess.commit()

                        session.clear()
                        session.permanent = False
                        session['id'] = new_user.id

                    else:
                        remember = session.pop('remember')
                        username = session.pop('username')

                        session.clear()
                        session.permanent = remember
                        if remember:
                            app.permanent_session_lifetime = timedelta(days=365)

                        user = db_sess.query(User).filter(User.username == username).first()
                        session['id'] = user.id

                    return redirect(url_for("base_win"))
                else:
                    flash("❌ Неверный код. Попробуйте снова.", "danger")
            else:
                flash("❌ Пожалуйста, введите код.", "danger")

        else:
            # Обновляем оставшееся время
            remaining_time = session.get('remaining_time', 300)

        email = session.get('email', None)
        # Отображаем страницу подтверждения с оставшимся временем
        return render_template(
            "mail_confirmation.html",
            form=form,
            authorization=typ,
            email=email,
            remaining_time=remaining_time
        )

    else:
        return redirect(url_for('error'))


@app.route("/update_time", methods=["GET", "POST"])
def update_time():
    if request.method == "POST":
        data = request.get_json()  # Получаем JSON данные из тела запроса
        remaining_time = data.get("remaining_time")

        # Обновляем оставшееся время в сессии
        session['remaining_time'] = remaining_time

        # Отправляем подтверждение успешного обновления
        return jsonify({"status": "success"})
    else:
        return redirect(url_for('error'))


@app.route("/time_limit/<authorization>", methods=["GET", "POST"])
def error_authorization(authorization):
    if request.method == "GET":
        session.clear()
        session.permanent = False
        return render_template("time_limit_authorization.html", authorization=authorization)
    else:
        return redirect(url_for('error'))


@app.route("/profile/<id>")
def profile(id):
    user_id = session.get('id', None)
    if user_id:
        load_dotenv()
        key = os.getenv("KEY")
        cipher = Fernet(key)

        id = int(cipher.decrypt(id.encode()).decode())

        user = db_sess.query(User).filter(User.id == id).first()

        avatar_data = base64.b64encode(user.avatar).decode('utf-8')
        avatar_url = f"data:image/png;base64,{avatar_data}"

        json_path = os.path.join('static', 'data', 'countries.json')

        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)
        countr = None
        for country in data:
            if country['code'] == user.country:
                countr = country['name']
                break

        dt = datetime.fromisoformat(str(user.created_date)).strftime("%d.%m.%Y %H:%M")

        if id == user_id:
            my_profile = True
        else:
            my_profile = False

        return render_template(
            "profile.html",
            user_authenticated=True,
            username=user.username,
            registration_date=dt,
            articles_count=user.article_count,
            email=user.email,
            country=countr,
            about_me=user.about_myself,
            user_id=id,
            my_profile=my_profile,
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

    load_dotenv()
    key = os.getenv("KEY")
    cipher = Fernet(key)

    user_id = cipher.encrypt(str(user_id).encode()).decode()

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
                return render_template(
                    "create_article.html",
                    form=form,
                    user_authenticated=True,
                    username=user.username,
                    avatar_url=avatar_url,
                    style=False,
                    title=title,
                    content=content,
                    font=font,
                    comments_allowed=comments_allowed,
                    user_id=user_id
                )

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
        user_id=user_id,
        form=form
    )


@app.route('/my_articles', methods=['POST', 'GET'])
def my_articles():
    pass


@app.route("/settings", methods=["GET", "POST"])
def settings():
    user_id = session.get('id', None)
    if user_id:
        user = db_sess.query(User).filter(User.id == user_id).first()
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
