from typing import Generic, Optional, Type, TypeVar

from sqlalchemy import delete, select, update

from core.db.sessions import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepo(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_by_id(self, id: int, session) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        data = await session.execute(query)
        return data.scalars().first()

    async def update_by_id(self, id: int, params: dict, session) -> None:
        query = update(self.model).where(self.model.id == id).values(**params)
        await session.execute(query)
        await session.commit()

    async def delete_by_id(self, id: int, session) -> None:
        query = delete(self.model).where(self.model.id == id)
        await session.execute(query)
        await session.commit()

    async def get_all(self, session):
        query = select(self.model)
        data = await session.execute(query)
        return data.scalars().all()
