from .ModelBase import Base
from typing import TypeVar
ModelType = TypeVar("ModelType", bound=Base)
from .Permission import Permission,Graphpermission,Roledisplayedmenu
from .User import User,UserRole
from .stock.Config import Config
from .stock.Strategy import Strategy