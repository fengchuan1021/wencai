import time

import Service
from Service.base import CRUDBase
import Models
from typing import Union, Dict
from datetime import datetime, timedelta
from jose import jwt
import settings
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from sqlalchemy.sql import or_
from typing import Optional
import hashlib
import random

from common.CommonError import ResponseException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from sqlalchemy import select


class UserService(CRUDBase[Models.User]):

    async def getUserByPhoneOrUsernameOrEmail(self, db: AsyncSession, usernameOrPhone: str) -> Optional[Models.User]:
        query = select(self.model).filter(
            or_(Models.User.username == usernameOrPhone, Models.User.phone == usernameOrPhone,
                Models.User.email == usernameOrPhone))
        results = await db.execute(query)
        return results.scalar_one_or_none()

    # dont delete we need use this in futchure
    # def verify_password(self,plain_password:str, hashed_password : Optional[str])->bool:
    #
    #     return pwd_context.verify(plain_password, hashed_password,'bcrypt')
    # def get_password_hash(self,password):# type: ignore
    #     return pwd_context.hash(password)
    def verify_password(self, password: str, dbpassword: str) -> bool:
        passwordhash, salthash = dbpassword.split(':')
        return passwordhash == hashlib.md5((salthash + password).encode()).hexdigest()

    def get_password_hash(self, password: str) -> str:
        salthash = hashlib.md5(random.randint(10000, 99999).to_bytes(4, byteorder='big')).hexdigest()
        passwordhash = hashlib.md5((salthash + password).encode()).hexdigest()
        return passwordhash + ':' + salthash

    async def authenticate(self, dbSession: AsyncSession, username: str, password: str) -> bool | Models.User:
        user = await self.getUserByPhoneOrUsernameOrEmail(dbSession, username)
        if not user:

            return False
        else:

            if not self.verify_password(password, user.password):  # type: ignore
                return False
        return user

    async def create_refresh_token(self, db: AsyncSession, data: Models.User, expires_delta: int = None) -> tuple[
        str, int]:
        to_encode = settings.UserTokenData.from_orm(data).dict()
        if expires_delta:
            expire = int(time.time()) + expires_delta
        else:
            expire = int(time.time()) + settings.REFRESH_TOKEN_EXPIRE_SECONDS
        to_encode.update({"exp": expire, 'type': 'refresh'})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt, expire

    async def create_access_token(self, db: AsyncSession, data: Models.User, expires_delta: int = None,
                                  extra_data: Dict = None) -> tuple[
        str, int]:
        merchant = await Service.merchantService.findOne(db, {'user_id': data.user_id})  # type: ignore

        to_encode = settings.UserTokenData.from_orm(data).dict()
        dic = {'merchant_id': merchant.merchant_id} if merchant else {}
        to_encode.update(dic)
        if expires_delta:
            expire = int(time.time()) + expires_delta
        else:
            expire = int(time.time()) + settings.ACCESS_TOKEN_EXPIRE_SECONDS
        to_encode.update({"exp": expire, 'type': 'access'})
        if extra_data:
            to_encode.update(extra_data)
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt, expire

    async def tokenFromRefreshToken(self, db: AsyncSession, refreshToken: str) -> tuple[str, int]:
        try:
            print('re:', refreshToken)
            payload = jwt.decode(refreshToken, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            print('pay:', payload)
            # data = settings.UserTokenData.parse_obj(payload)
            if payload['type'] != 'refresh':
                raise Exception("not refresh token")
            print('222')
            user = await self.findByPk(db, payload['user_id'])
            if not user:
                raise Exception("user not found")
            return await self.create_access_token(db, user)

        except Exception as e:
            raise Exception("refresh token is invalid")


if __name__ == '__main__':
    import asyncio
    from component.dbsession import getdbsession


    async def t() -> None:
        async with getdbsession() as db:
            result = Service.userService.get_password_hash('unineedRoot@#189')
            print(result)


    asyncio.run(t())
