from component.snowFlakeId import snowFlack
from sqlalchemy import Column, text
from sqlalchemy.dialects.mysql import BIGINT, ENUM, INTEGER, DECIMAL, TEXT
from sqlalchemy.orm import relationship

from Models.ModelBase import Base, XTVARCHAR
from typing import TYPE_CHECKING




class Config(Base):
    __tablename__ = 'config'
    config_id = Column(BIGINT(20), primary_key=True, default=snowFlack.getId)
    config_name = Column(XTVARCHAR(32), unique=True)
    config_value=Column(TEXT)

    gp=Column(ENUM('basic','front','default'),default='basic',server_default='basic')