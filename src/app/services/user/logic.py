from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import UnmappedInstanceError

from app.services.user import schemes
from core.auth import AuthHandler
from core.exceptions.server import ServerError
from core.exceptions.user import (UserDoesNotExists, UserWithSameEmailExists,
                                  UserWithSameLoginExists, )
from core.repository.base import BaseRepo


class UserLogic(BaseRepo):
    def __init__(self, model):
        self.auth_handler = AuthHandler()
        super(UserLogic, self).__init__(model)
    async def get_user_by_id(self, db: Session, user_id: int):
        query = select(self.model).where(self.model.id == user_id)
        r = await db.execute(query)
        return r.scalars().first()

    async def get_user_by_email(self, db: Session, email: str):
        query = select(self.model).where(self.model.email == email)
        r = await db.execute(query)
        return r.scalars().first()

    async def get_user_by_login(self, db: Session, username: str):
        query = select(self.model).where(self.model.username == username)
        r = await db.execute(query)
        return r.scalars().first()

    async def delete_user(self, db: Session, username: str):
        if not await self.get_user_by_login(username=username, db=db):
            return False, UserDoesNotExists
        record = select(self.model).where(self.model.username == username)
        record = await db.execute(record)
        record = record.scalars().first()
        try:
            await db.delete(record)
            await db.commit()
        except UnmappedInstanceError:
            return False, ServerError
        return True, None

    async def create_user(self, password: str, db: Session, user: schemes.UserCreate):

        try:
            if await self.check_email(user.email, db):
                return False, UserWithSameEmailExists
            elif await self.check_login(user.username, db):
                return False, UserWithSameLoginExists
            hashed_password = await self.auth_handler.get_passwords_hash(password)
            data = user.dict()
            data["password"] = hashed_password
            db_user = self.model(**data)
            db.add(db_user)

            await db.commit()
            await db.refresh(db_user)
        except Exception as exc:
            print(exc)
            return False, ServerError
        return True, db_user

    async def check_login(self, login: str, db: Session):
        if await self.get_user_by_login(db, login):
            return True
        return False

    async def check_email(self, email: str, db: Session):
        if await self.get_user_by_email(db, email):
            return True
        return False

    async def patch_user(self, db: Session, user: schemes.UserPatch, username: str):
        try:
            db_user = select(self.model).where(self.model.username == username)
            db_user = await db.execute(db_user)
            db_user = db_user.scalars().first()
            res = await self.check_login(login=username, db=db)
            if not res:
                return False, UserDoesNotExists
            if user.password is not None:
                hashed_password = await self.auth_handler.get_passwords_hash(user.password)
                user.password = hashed_password

            query = update(self.model).where(self.model.username == username).values(**user.dict())
            await db.execute(query)
            await db.commit()
        except Exception as exc:
            return False, ServerError
        return True, user
