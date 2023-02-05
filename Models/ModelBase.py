import orjson
from sqlalchemy.orm import deferred
from sqlalchemy import Column, DateTime, text
import settings
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.ext.declarative import declared_attr

from typing import Any, Dict, List, Optional
from sqlalchemy.ext.hybrid import hybrid_property

import sqlalchemy.types as types
import os
from decimal import Decimal
from XTTOOLS import obj2dict
from sqlalchemy.dialects.mysql import INTEGER
from component.snowFlakeId import snowFlack

if int(os.getenv('migratedb', 0)):
    from sqlalchemy.dialects.mysql import VARCHAR as XTVARCHAR  # type: ignore
else:
    class XTVARCHAR(types.TypeDecorator):  # type: ignore
        impl = types.String
        cache_ok = True

        def process_bind_param(self, value: str, dialect: Any) -> str:  # type: ignore
            if settings.AUTO_TRUNCATE_COLUMN:
                if not value:
                    return value
                if isinstance(value, int):
                    return str(value)[:self.impl.length]
                return value[:self.impl.length]
            else:
                return value

        def copy(self, **kwargs: Any) -> 'XTVARCHAR':  # type: ignore
            return XTVARCHAR(self.impl.length)  # type: ignore


class MyBase(object):
    @declared_attr
    def __mapper_args__(cls):
        return {"version_id_col": cls.version}

    @hybrid_property
    def id(self):  # type: ignore
        return getattr(self, f'{self.__tablename__}_id')

    @declared_attr
    def created_at(self) -> Column[DateTime]:
        return Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
        # return deferred(Column(DateTime, server_default=text("CURRENT_TIMESTAMP")))

    @declared_attr
    def updated_at(self) -> Column[DateTime]:
        return Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    @declared_attr
    def version(self) -> Column[INTEGER]:
        return Column(INTEGER, nullable=False, default='1', server_default='1')

    def dict(self, resolved: List['MyBase'] = None, exclude=None) -> Dict[str, Any]:  # type: ignore
        if resolved == None:
            resolved = []
        dic = {}
        if self not in resolved:  # type: ignore
            resolved.append(self)  # type: ignore
        for key, value in self.__dict__.items():
            if exclude and key in exclude:
                continue
            if key.startswith('_'):
                continue
            if isinstance(value, Base):
                if value not in resolved:  # type: ignore
                    dic[key] = value.dict(resolved)
            elif isinstance(value, list):
                dic[key] = [v.dict(resolved) for v in value]  # type: ignore

            else:
                dic[key] = value
        return dic

    def json(self) -> str:
        return orjson.dumps(self.dict(), default=obj2dict).decode()


def xt_constructor(instance, **kwds) -> None:  # type: ignore

    primaryname = getattr(instance, "__tablename__") + '_id'
    pkcolumn = getattr(type(instance), primaryname)
    if pkcolumn.default:
        setattr(instance, primaryname, snowFlack.getId())
    for attr, value in kwds.items():
        setattr(instance, attr, value)


Base = declarative_base(cls=MyBase, constructor=xt_constructor)
