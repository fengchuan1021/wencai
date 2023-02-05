#   timestamp: 2022-10-03T11:35:27+00:00

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, Literal

from pydantic import BaseModel, constr, validator, Field


class FrontendUserRegisterPostInShema(BaseModel):
    username: Optional[str] = None  # type: ignore
    password: str
    # repassword: str = Field(..., exclude=True)
    phone: Optional[str] = None
    email: constr(min_length=4, max_length=64)  # type: ignore
    verifycode: str

    # @validator('repassword')
    # def passwords_match(cls, v, values, **kwargs):  # type: ignore
    #     if 'password' in values and v != values['password']:
    #         raise ValueError('passwords do not match')
    #     return v


class User(BaseModel):
    username: str
    phone: str
    email: str

    class Config:
        orm_mode = True


class FrontendUserLoginPostInShema(BaseModel):
    username: str
    password: str
