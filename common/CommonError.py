from typing import Dict

from pydantic import BaseModel
from typing import TypeVar, Generic, Optional, List, Any, Literal
from .CommonResponse import CommonResponse


class Common500Response(BaseModel):
    errorcode: int = 500
    errormsg: Optional[str] = ''
    data: Optional[Any]


class TokenException(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    def __repr__(self) -> str:
        return self.msg

    def __str__(self) -> str:
        return self.msg


class PermissionException(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    def __repr__(self) -> str:
        return self.msg

    def __str__(self) -> str:
        return self.msg


class ResponseException(Exception):
    def __init__(self, response: Dict):
        if 'errormsg' not in response:
            response['errormsg'] = ''
        if 'errorcode' not in response:
            response['errorcode'] = 200
        self.response = response

    def __repr__(self) -> str:
        return self.response['errormsg']

    def __str__(self) -> str:
        return self.response['errormsg']
