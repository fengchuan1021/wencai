#dont modfiy this file!!! it generate from devtools/template/Service__init__.py.tpl
#dont modfiy this file!!! it generate from devtools/template/Service__init__.py.tpl
import os
from typing import Any,TypeVar,TYPE_CHECKING
import Models
import sys
from common.findModelByName import findModelByName
import settings
import typing
thismodule = sys.modules[__name__]
from .base import CRUDBase
ModelType = TypeVar("ModelType", bound=Models.Base)

from .UploadService import UploadService
from .backend.MailService import MailService
from .backend.PermissionService import PermissionService
from .sina.SinaService import SinaService
from .tushare.TuShareService import TuShareService
from .user.UserService import UserService
from .wencai.WenCaiService import WenCaiService


def __getattr__(name: str) -> Any:

    lowername=name.replace('Service','')
    for i in lowername:
        if not 97<=ord(i)<=122:
            raise Exception("service name should be all lowercase")
    for annotationname,classtype in thismodule.__annotations__.items():

        if annotationname==name:

            if isinstance(classtype,typing._GenericAlias) or issubclass(classtype,CRUDBase):#type: ignore
                tmpinstance = classtype(model:=findModelByName(lowername),model.__name__ in settings.cache_models)#type: ignore
            else:
                tmpinstance = classtype()
            setattr(thismodule, name, tmpinstance)
            return tmpinstance

    raise Exception(f'not found {name}')

permissionService : PermissionService
graphpermissionService : CRUDBase[Models.Graphpermission]
roledisplayedmenuService : CRUDBase[Models.Roledisplayedmenu]
userService : UserService
userroleService : CRUDBase[Models.UserRole]
configService : CRUDBase[Models.Config]
strategyService : CRUDBase[Models.Strategy]
uploadService : UploadService
mailService : MailService
sinaService : SinaService
tushareService : TuShareService
wencaiService : WenCaiService