from pydantic import BaseModel


class PostBase(BaseModel):
    title: str = "Название поста"
    body: str = "Текст поста"
