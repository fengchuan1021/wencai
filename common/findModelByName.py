from functools import lru_cache
import Models

from typing import Type
@lru_cache(maxsize=None)
def findModelByName(name:str)->Type[Models.ModelType]:

    if tmp:=getattr(Models,name.upper()+name[1:],None):

        return tmp
    for tmpname,value in Models.__dict__.items():
        if not 65<=ord(tmpname[0])<=90:
            continue
        if tmpname.lower()==name.lower():
            return value
    raise Exception(f'model not found {name}')
