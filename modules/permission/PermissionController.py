from __future__ import annotations

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from component.dbsession import get_webdbsession
import Service
from component.cache import cache
from fastapi import APIRouter, Depends, Body
from sqlalchemy.exc import IntegrityError
import settings
from typing import Dict, Any, List
from common import get_token, CommonResponse, XTJsonResponse
from common.findModelByName import findModelByName
from common import CommonError
import Models

from imp import reload
import os
from .__init__ import dependencies

router = APIRouter(dependencies=dependencies)


# <editor-fold desc="allmodel">
@router.get(
    '/permission/allmodel',

    response_model=CommonResponse,
)
async def allmodel(
        db: AsyncSession = Depends(get_webdbsession),
        token: settings.UserTokenData = Depends(get_token),
) -> Any:
    """
    allmodel
    """
    models = []
    for name, class_ in Models.__dict__.items():
        if ord('A') <= ord(name[0]) <= ord('Z'):
            try:
                if issubclass(class_, Models.Base):
                    models.append(name)
            except Exception as e:
                pass

    # install pydantic plugin,press alt+enter auto complete the args.
    return {'errorcode': 200,
            'errormsg': '',
            'data': models
            }


# </editor-fold>


# <editor-fold desc="modelcolumns">
@router.get(
    '/permission/modelcolumns/{modelname}',

    response_model=CommonResponse,
)
async def modelcolumns(
        modelname: str,
        db: AsyncSession = Depends(get_webdbsession),
        token: settings.UserTokenData = Depends(get_token),
) -> Any:
    """
    modelcolumns
    """
    modelClass = findModelByName(modelname)
    data = [c.name for c in modelClass.__table__.columns]  # type: ignore

    # install pydantic plugin,press alt+enter auto complete the args.

    return {'errorcode': 200,
            'errormsg': '',
            'data': data
            }


# </editor-fold>

# <editor-fold desc="setrolemodelpermission">
from .PermissionShema import PermissionSetrolemodelpermissionPostRequest


@router.post(
    '/permission/setrolemodelpermission',
)
async def setrolemodelpermission(
        body: PermissionSetrolemodelpermissionPostRequest,
        db: AsyncSession = Depends(get_webdbsession),
        token: settings.UserTokenData = Depends(get_token),
) -> Any:
    """
    setrolemodelpermission
    """

    body.read_columns = ','.join(body.read_columns)  # type: ignore
    body.write_columns = ','.join(body.write_columns)  # type: ignore
    body.update_columns = ','.join(body.update_columns)  # type: ignore
    body.delete_columns = ','.join(body.delete_columns)  # type: ignore
    body.notify_columns = ','.join(body.notify_columns)  # type: ignore
    body.read_extra = ','.join(body.read_columns)  # type: ignore
    body.write_extra = ','.join(body.write_columns)  # type: ignore
    body.update_extra = ','.join(body.update_columns)  # type: ignore
    body.delete_extra = ','.join(body.delete_columns)  # type: ignore

    await Service.graphpermissionService.create(db, body)
    await db.commit()
    return {'status': 0}


# </editor-fold>


# <editor-fold desc="getroutelist">
@router.get(
    '/permission/routes',

)
async def getroutelist(
        db: AsyncSession = Depends(get_webdbsession),
        token: settings.UserTokenData = Depends(get_token),
) -> Any:
    """
    getroutelist
    """
    routes = await Service.permissionService.getroutelist()

    def tolist(tmp: Dict) -> None:
        if 'children' in tmp:
            tmp['children'] = list(tmp['children'].values())
            for item in tmp['children']:
                tolist(item)

    tolist(routes)
    print('routes:', routes)
    return routes


# </editor-fold>


# <editor-fold desc="setrolepermission">
@router.post(
    '/permission/setrolepermission',

)
async def setrolepermission(
        body: Dict = Body(...),
        db: AsyncSession = Depends(get_webdbsession),
        token: settings.UserTokenData = Depends(get_token),
) -> Any:
    """
    setrolepermission
    """
    if 'role_id' not in body:
        return {'errorcode': 500, 'errormsg': 'role_id not provided'}
    if 'apis' not in body:
        return {'errorcode': 500, 'errormsg': 'apis not provided'}

    await Service.permissionService.setUserRolePermission(db, body['role_id'], body['role_name'], body['apis'])
    # install pydantic plugin,press alt+enter auto complete the args.
    return {'status': 'success'}


# </editor-fold>


# <editor-fold desc="admingetroledisplayedmenu">
@router.get(
    '/backend/permission/admingetroledisplayedmenu',

)
async def admingetroledisplayedmenu(
        role_id: int,
        db: AsyncSession = Depends(get_webdbsession),
        token: settings.UserTokenData = Depends(get_token),
) -> Any:
    """
    getroledisplayedmenu
    """
    result = await Service.permissionService.getroledisplayedmenu(db, role_id)
    return {'status': 'success', 'data': [r.menu_path for r in result]}


# </editor-fold>


# <editor-fold desc="setroledisplayedmenu">
class BackendPermissionSetdisplayedmenuPostRequest(BaseModel):
    role_id: int
    menus: List[str]


@router.post(
    '/permission/setdisplayedmenu',
)
async def setroledisplayedmenu(
        body: BackendPermissionSetdisplayedmenuPostRequest,
        db: AsyncSession = Depends(get_webdbsession),
        token: settings.UserTokenData = Depends(get_token),
) -> Any:
    """
    setroledisplayedmenu
    """
    await Service.permissionService.setRoleDisplayedMenu(db, body.role_id, body.menus)
    # install pydantic plugin,press alt+enter auto complete the args.
    return {'status': 'success'}

# </editor-fold>
