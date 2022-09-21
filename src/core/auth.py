from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

from core.config import settings
from core.repository.base import BaseRepo
from app.services.user.models import Users
from core.db.sessions import session_local


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = settings.SECRET
    repo = BaseRepo(Users)

    async def get_passwords_hash(self, password):
        return self.pwd_context.hash(password)

    async def verify_password(self, plain_password, hash_password):
        return self.pwd_context.verify(plain_password, hash_password)

    async def encode_token(self, user_id):
        payload = {
            "exp": datetime.utcnow() + timedelta(minutes=10),
            "iat": datetime.utcnow(),
            "id": user_id,
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")

    async def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])
            async with session_local() as session:
                if not await self.repo.get_by_id(payload.get('id'),session):
                    raise HTTPException(status_code=401, detail="Token is invalid")
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Signature has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Token is invalid")

    async def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return await self.decode_token(auth.credentials)
