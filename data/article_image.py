import sqlalchemy
from sqlalchemy import LargeBinary
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase


class ArticleImage(SqlAlchemyBase):
    __tablename__ = 'article_images'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    image_data = sqlalchemy.Column(LargeBinary, nullable=False)  # Теперь сохраняем бинарные данные

    article_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('articles.id'))
    article = relationship("Article", back_populates="images")

    def __repr__(self):
        return f"<ArticleImage id={self.id}>"
