import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship

from core.db.sessions import Base


class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    body = Column(String)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"))
    children = relationship("Likes", back_populates="post")


class Likes(Base):
    __tablename__ = "like"
    post_id = Column(ForeignKey("post.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    date_of_like = Column(Date, default=datetime.date)

    user = relationship("Users", back_populates="parents")
    post = relationship("Post", back_populates="children")
