import datetime

from sqlalchemy import select, delete
from sqlalchemy import and_

from app.services.post.models import Likes
from core.repository.base import BaseRepo


class PostLogic(BaseRepo):
    def __init__(self, model):
        super(PostLogic, self).__init__(model)
        self.likes = BaseRepo(Likes)
        pass

    async def create_post(self, post: dict, db, user_id):
        post.update({"user_id": user_id})
        post_instance = self.model(**post)
        db.add(post_instance)
        await db.commit()
        await db.refresh(post_instance)
        return post_instance

    async def get_likes(self, date_from, date_to, db):
        query = select(Likes).filter(and_(Likes.date_of_like >= date_from, Likes.date_of_like <= date_to))
        q = await db.execute(query)
        res = q.scalars().all()

        likes_by_dates = {}
        for i in res:
            if not likes_by_dates.get(i.date_of_like):
                likes_by_dates.update({i.date_of_like: []})
            likes_by_dates[i.date_of_like].append(
                {
                    "user_id": i.user_id,
                    "post_id": i.post_id

                }
            )
        return likes_by_dates

    async def get_like(self, db, post_id, user_id):
        query = select(Likes).where(and_(Likes.user_id == user_id, Likes.post_id == post_id))
        r = await db.execute(query)
        return r.scalars().first()

    async def like_post(self, post_id, user_id, db):

        like_instance = Likes(post_id=post_id, user_id=user_id, date_of_like=datetime.date.today())
        db.add(like_instance)
        await db.commit()
        await db.refresh(like_instance)

    async def unlike_post(self, post_id, user_id, db):
        query = delete(Likes).where(and_(Likes.user_id == user_id, Likes.post_id == post_id))
        await db.execute(query)
        await db.commit()
