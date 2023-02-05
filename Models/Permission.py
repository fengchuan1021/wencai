from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.dialects.mysql import INTEGER, BIGINT, ENUM
from sqlalchemy.orm import relationship, foreign

from .ModelBase import Base, XTVARCHAR
import typing

if typing.TYPE_CHECKING:
    from .User import User


class Permission(Base):
    __tablename__ = 'permission'
    __table_args__ = (UniqueConstraint('role_id', "api_name", name="roleapi"),)
    permission_id = Column(INTEGER, autoincrement=True, primary_key=True)
    role_id = Column(INTEGER, index=True)
    role_name = Column(XTVARCHAR(32))
    api_name = Column(XTVARCHAR(255), comment="routes array the role has permission to access. ")


class Graphpermission(Base):
    __tablename__ = 'graphpermission'
    __table_args__ = (UniqueConstraint('role_id', "model_name", name="rolemodelname"),)
    graphpermission_id = Column(INTEGER, autoincrement=True, primary_key=True)
    model_name = Column(XTVARCHAR(32), nullable=False)
    read_columns = Column(XTVARCHAR(512), default='')
    write_columns = Column(XTVARCHAR(512), default='')
    update_columns = Column(XTVARCHAR(512), default='')
    delete_columns = Column(ENUM("N", 'Y'), default='N')
    notify_columns = Column(ENUM("N", 'Y'), default='N', index=True)
    role_id = Column(INTEGER)
    role_name = Column(XTVARCHAR(32), default='')
    read_extra = Column(XTVARCHAR(512), default='')
    write_extra = Column(XTVARCHAR(512), default='')
    update_extra = Column(XTVARCHAR(512), default='')
    delete_extra = Column(XTVARCHAR(512), default='')


class Roledisplayedmenu(Base):
    __tablename__ = 'roledisplayedmenu'
    __table_args__ = (UniqueConstraint('merchant_id', 'role_id', "menu_path", name="roledispplayedmenu"),)
    roledisplayedmenu_id = Column(INTEGER, autoincrement=True, primary_key=True)
    role_id = Column(BIGINT)
    role_name = Column(XTVARCHAR(32))
    merchant_id = Column(BIGINT, default=0, server_default='0')
    menu_path = Column(XTVARCHAR(32))
