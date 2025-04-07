import sqlalchemy
from datetime import datetime
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow)

    country = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    with open('static/img/default.jpg', 'rb') as file:
        img = file.read()



    avatar = sqlalchemy.Column(sqlalchemy.LargeBinary, default=img)
