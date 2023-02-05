from typing import Literal, Optional, Any, Dict

from pydantic import BaseModel


class CommonQueryShema(BaseModel):
    pagesize: Optional[int] = 20
    pagenum: Optional[int] = 1
    filter: Optional[Dict] = None


class CommonResponse(BaseModel):
    errorcode: int
    errormsg: Optional[str] = ''
    data: Optional[Any]
    total: Optional[int]
