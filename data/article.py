import sqlalchemy
from sqlalchemy.orm import relationship
from datetime import datetime
from .db_session import SqlAlchemyBase


class Article(SqlAlchemyBase):
    __tablename__ = 'articles'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    font = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    comments_allowed = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow)

    likes = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=False)
    views = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=False)

    # Связь с таблицей изображений
    images = relationship("ArticleImage", back_populates="article", cascade="all, delete-orphan")

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user = relationship('User')

    def __repr__(self):
        return f"<Article {self.title}>"
