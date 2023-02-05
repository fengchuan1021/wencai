from component.snowFlakeId import snowFlack
from sqlalchemy import Column, text
from sqlalchemy.dialects.mysql import BIGINT, ENUM, INTEGER, DECIMAL, TEXT
from sqlalchemy.orm import relationship

from Models.ModelBase import Base, XTVARCHAR
from typing import TYPE_CHECKING




class Strategy(Base):
    __tablename__ = 'strategy'

    strategy_id = Column(BIGINT(20), primary_key=True, default=snowFlack.getId)
    strategy_name = Column(XTVARCHAR(32), nullable=True, unique=True)
    content=Column(TEXT, nullable=False)
    delay=Column(INTEGER, nullable=False, default=5,server_default='5')