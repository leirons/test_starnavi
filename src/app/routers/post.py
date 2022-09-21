import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemes import Message
from app.services.post import schemes
from app.services.post.logic import PostLogic
from app.services.post.models import Post
from core import auth
from core.cache.backend import RedisBackend
from core.cache.cache import CacheManager
from core.cache.key_marker import CustomKeyMaker
from core.db.sessions import get_db
from core.exceptions.post import PostDoesNotExists, LikeAlreadyExists, LikeDoesNotExists

router = APIRouter()
logic = PostLogic(model=Post)

auth_handler = auth.AuthHandler()

cache_manager = CacheManager(backend=RedisBackend(), key_maker=CustomKeyMaker())


@router.post(
    "/post/create_post",
    tags=["post"],
    status_code=status.HTTP_201_CREATED,
    response_model_exclude={"id"},
    response_model=schemes.PostBase
)
async def create_post(post: schemes.PostBase, db: Session = Depends(get_db), user=Depends(auth_handler.auth_wrapper)):
    res = await logic.create_post(db=db, post=post.dict(), user_id=user.get('id'))
    return res.__dict__


@router.post(
    "/post/like_post",
    tags=["post"],
    status_code=status.HTTP_201_CREATED,
    responses={
        403: {"model": Message},
        409: {"model": Message},

    },
)
async def like_post(post_id: int, db: Session = Depends(get_db), user=Depends(auth_handler.auth_wrapper)):
    if await logic.get_like(post_id=post_id, user_id=user.get('id'), db=db):
        raise HTTPException(detail=LikeAlreadyExists.message, status_code=LikeAlreadyExists.error_code)

    res = await logic.get_by_id(id=post_id, session=db)
    if not res:
        raise HTTPException(detail=PostDoesNotExists.message, status_code=PostDoesNotExists.error_code)
    await logic.like_post(post_id=post_id, user_id=user.get('id'), db=db)
    return {'operation': "succeed"}


@router.post(
    "/post/unlike_post",
    tags=["post"],
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": Message},
    },
)
async def unlike_post(post_id: int, db: Session = Depends(get_db), user=Depends(auth_handler.auth_wrapper)):
    res = await logic.get_by_id(id=post_id, session=db)

    if await logic.get_like(post_id=post_id, user_id=user.get('id'), db=db):
        raise HTTPException(detail=LikeDoesNotExists.message, status_code=LikeDoesNotExists.error_code)

    if not res:
        raise HTTPException(detail=PostDoesNotExists.message, status_code=PostDoesNotExists.error_code)
    await logic.unlike_post(post_id=post_id, user_id=user.get('id'), db=db)
    return {'operation': "succeed"}


@router.get(
    "/post/get_likes",
    tags=["post"],
    status_code=status.HTTP_200_OK,
)
async def get_likes(date_from: datetime.date, date_to: datetime.date, db: Session = Depends(get_db)):
    return await logic.get_likes(date_from, date_to, db)


@router.get(
    "/post/get_post",
    tags=["post"],
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": Message},
    },
)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    res = await logic.get_by_id(id=post_id, session=db)
    if not res:
        raise HTTPException(detail=PostDoesNotExists.message, status_code=PostDoesNotExists.error_code)
    return res.__dict__
