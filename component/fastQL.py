from typing import Any, Dict, Optional

from sqlalchemy import text, func
from sqlalchemy.ext.asyncio import AsyncSession

import Service
import settings
from common import PermissionException
from common.findModelByName import findModelByName
from common.filterbuilder import filterbuilder
from component.graphqlpermission import getAuthorizedColumns
from component.sqlparser import parseSQL, getmodelnamecloums
from typing import List
from component.cache import cache


async def fastQuery(db: AsyncSession,
                    query: str,
                    filter: Dict = None,
                    pagenum: int = 0,
                    pagesize: int = 0,
                    orderby: str = '',
                    returntotal: bool = False,
                    context: Optional[settings.UserTokenData] = None,
                    returnsingleobj: bool = False,
                    ) -> Any:
    if query[-1] != '}':
        query = query + '{}'

    where, params = filterbuilder(filter)
    statment = (await parseSQL(query, db, context)).where(text(where))

    total = None
    if returntotal:
        count_statment = statment.with_only_columns([func.count()], maintain_column_froms=True)
        total = (await db.execute(count_statment, params)).scalar()
    print("debug0", statment)
    if pagesize and pagenum:
        statment = statment.offset((pagenum - 1) * pagesize).limit(pagesize)
    if orderby:
        statment = statment.order_by(text(orderby))
    print("debug1", statment)
    results = await db.execute(statment, params)

    data = results.scalars().unique().all()

    if returnsingleobj:
        return data[0] if data else None
    if returntotal == False:
        return data
    return data, total


async def _fastAdd(db: AsyncSession, modelname: str, data: Dict,
                   context: Optional[settings.UserTokenData] = None) -> Any:
    '''context 来指定用什么用户角色来添加数据'''
    '''context 里边role_id为商家 即以商家角色添加数据'''
    '''getAuthorizedColumns去权限表里边查找商家能读取/写入的字段'''
    columns = ['*']
    extra = []
    allpermission = False
    if context:
        columns, extra = await getAuthorizedColumns(db, modelname, context.role_id, method='write')
    if '*' in columns:
        allpermission = True

    dic = {}
    modelclass = findModelByName(modelname)
    children = {}

    _lowerrelation = [i.lower() for i in columns if 'A' <= i[0] <= 'Z']
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            if not allpermission and key.lower() not in _lowerrelation:
                raise PermissionException(f"not permission access {key}")
            if isinstance(value, list):
                children[key] = modelclass.__annotations__.get(key).__args__[0].__forward_arg__  # type: ignore
            else:
                children[key] = modelclass.__annotations__.get(key)
        else:
            if not allpermission and key not in columns:
                raise PermissionException(f"not permission access {key}")
            dic[key] = value

    if context:
        dic.update({i: getattr(context, i) for i in extra})
    model = modelclass(**dic)
    for child in children:
        if isinstance(data[child], dict):
            data[child][modelname + "_id"] = model.id
            submodel = await _fastAdd(db, children[child], data[child], context)  # type: ignore
            setattr(model, child, submodel)
        else:
            attribute = getattr(model, child)
            for tmpdata in data[child]:
                tmpmodel = await _fastAdd(db, children[child], tmpdata, context)  # type: ignore
                attribute.append(tmpmodel)
    return model


async def fastAdd(db: AsyncSession, modelname: str, data: Dict,
                  context: Optional[settings.UserTokenData] = None) -> Any:
    model = await _fastAdd(db, modelname, data, context)
    db.add(model)
    return model


async def fastDel(db: AsyncSession, modelname: str, id: int = 0, context: Optional[settings.UserTokenData] = None,
                  extra_filter: Dict = None) -> Any:
    extra = []
    if context and context.role_id != 1:
        columns, extra = await getAuthorizedColumns(db, modelname, context.role_id, method='delete')
        if columns[0] != 'Y':
            return False  # no permission
    if service := getattr(Service, modelname + 'Service', None):
        tmpdic = {i: getattr(context, i) for i in extra}
        if extra_filter:
            tmpdic.update(extra_filter)
        if id:
            await service.deleteByPk(db, id, tmpdic)
        else:
            models = await service.find(db, tmpdic)
            for model in models:
                await fastDel(db, modelname, model.id, context, extra_filter)
    else:
        raise Exception(f"{modelname} not found")
        return False

    return True


if __name__ == '__main__':
    from component.dbsession import getdbsession
    from common import cmdlineApp
    from settings import UserTokenData
    from sqlalchemy import select, text
    from sqlalchemy.orm import aliased
    from sqlalchemy.orm import joinedload, load_only, contains_eager
    from XTTOOLS import toJson
    import orjson
    import Models


    @cmdlineApp
    async def test(db):  # type: ignore
        # user1=aliased(Models.Category)
        query = "category{category_id,category_name,Children{}}"
        # a=aliased(Models.Category)
        # s=select(Models.Category).join(Models.Category.Children.of_type(a)).options(contains_eager(Models.Category.Children,alias=a))
        # print(s)
        ret = await fastQuery(db, query)
        print(toJson(ret))


    test()
