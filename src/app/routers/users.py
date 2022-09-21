from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.schemes import Message
from app.services.user import schemes
from app.services.user.logic import UserLogic
from app.services.user.models import Users
from core import auth
from core.cache.backend import RedisBackend
from core.cache.cache import CacheManager
from core.cache.key_marker import CustomKeyMaker
from core.db.sessions import get_db
from core.exceptions.user import PasswordOrLoginDoesNotMatch, UserDoesNotExists, UserWithSameLoginExists

router = APIRouter()
logic = UserLogic(model=Users)
auth_handler = auth.AuthHandler()

cache_manager = CacheManager(backend=RedisBackend(), key_maker=CustomKeyMaker())


@router.get("/user/refresh_token", tags=["user"], response_model=schemes.UserToken)
async def refresh_token(request: Request, db: Session = Depends(get_db), user=Depends(auth_handler.auth_wrapper)):
    # TODO We could use redis for storing all tokens and delete useless

    return {"token": await auth_handler.encode_token(user_id=request.user.id)}


@router.post(
    "/user/create_user",
    tags=["user"],
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"model": Message},
    },
    response_model_exclude={"id"},
    response_model=schemes.User
)
async def create_user(user: schemes.UserCreate, db: Session = Depends(get_db)):
    operation, res = await logic.create_user(db=db, user=user, password=user.password)
    if not operation:
        raise HTTPException(detail=res.message, status_code=res.error_code)
    return res.__dict__


@router.post(
    "/user/login",
    tags=["user"],
    responses={401: {"model": Message}},
    status_code=status.HTTP_200_OK,
    response_model=schemes.UserToken
)
async def login(user: schemes.UserLogin, db: Session = Depends(get_db)):
    user_old = await logic.get_user_by_login(db, user.username)
    if user_old and await auth_handler.verify_password(
            plain_password=user.password, hash_password=user_old.password
    ):
        token = await auth_handler.encode_token(user_old.id)
        return {"token": token}
    raise HTTPException(
        status_code=PasswordOrLoginDoesNotMatch.error_code,
        detail=PasswordOrLoginDoesNotMatch.message,
    )


@router.delete(
    "/user/{username}",
    tags=["user"],
    responses={404: {"model": Message}},
    status_code=status.HTTP_200_OK,
)
async def delete_user(username: str, request: Request, db: Session = Depends(get_db)):
    operation, res = await logic.delete_user(db, username=username)
    if not operation:
        raise HTTPException(detail=res.message, status_code=res.error_code)
    return res


@router.get(
    "/user/{username}", response_model=schemes.User, tags=["user"], status_code=status.HTTP_200_OK
)
async def get_user_by_username(
        username: str,
        db: Session = Depends(get_db),
):
    res = await logic.get_user_by_login(db, username)
    if not res:
        raise HTTPException(status_code=UserDoesNotExists.error_code, detail=UserDoesNotExists.message)
    return res

@router.patch(
    "/user/{username}",
    tags=["user"],
    responses={404: {"model": Message}},
    status_code=status.HTTP_200_OK,
)
async def patch_user(
        username: str, user: schemes.UserPatch, db: Session = Depends(get_db)
):
    res = await logic.get_user_by_login(db, user.username)
    if res:
        raise HTTPException(status_code=UserWithSameLoginExists.error_code, detail=UserWithSameLoginExists.message)

    operation, res = await logic.patch_user(db=db, user=user, username=username)

    if not operation:
        raise HTTPException(detail=res.message, status_code=res.error_code)
    return res
