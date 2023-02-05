import random
from functools import wraps
from typing import Optional, TypeVar, Callable, Any, cast

from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.orm.exc import StaleDataError



F = TypeVar('F', bound=Callable[..., Any])


def retrylock(__func:F) -> F:
    '''
    没有考虑嵌套的情况。FUN_A 带有retry装饰器 FUN_A 中调用带有retrylock的FUN_B 如果B出错重试 A中的事物也会被撤销
    可以用save_point 解决回滚的作用域，但是一般情况的需求是 FUN_A FUN_B 整体保持一致。所以事物全部回滚。
    '''

    @wraps(__func)
    async def inner(*args: Any, **kwargs: Any) -> Any:
        db=args[1]
        n=3
        while n>0:
            try:

                result=await __func(*args, **kwargs)
                await db.flush()
                return result
            except StaleDataError as e:
                await db.rollback()
                print("data dirty,retry again")
                n-=1
                if n==0:
                    raise e



    return cast(F, inner)


    return inner
def test()->None:
    from common import cmdlineApp
    import Service,random,asyncio,threading
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.orm import scoped_session
    from sqlalchemy.ext.asyncio import create_async_engine



    def testupdatefailed()->Any:#type: ignore
        '''测试不加锁多线程更新同一个订单 乐观锁报错'''
        async def updateorder(order_id:int=61821984346146)->Any:
            from sqlalchemy.ext.asyncio import AsyncSession
            ASYNCDBURL = "mysql+aiomysql://root:6zZjywcDt7AcI3oI@62.100.206.108:3306/fengchuanxt?charset=utf8mb4"
            async_session_factory = sessionmaker(class_=AsyncSession, bind=create_async_engine(ASYNCDBURL, echo=True))
            AsyncSession = async_scoped_session(async_session_factory, scopefunc=asyncio.current_task)#type: ignore
            async with AsyncSession() as db:

                while 1:
                    order=await Service.orderService.findByPk(db,order_id)
                    order.market_name=str(random.randint(100,2000))
                    await asyncio.sleep(0.1)
                    await db.commit()
        loop=asyncio.new_event_loop()
        loop.run_until_complete(updateorder(61821984346146))


    def testupdatefailedretry()->Any:#type: ignore
        '''多加一个装饰器 测试重试'''

        @retrylock
        async def updateorder(order_id:int=61821984346146)->Any:
            from sqlalchemy.ext.asyncio import AsyncSession
            ASYNCDBURL = "mysql+aiomysql://root:6zZjywcDt7AcI3oI@62.100.206.108:3306/fengchuanxt?charset=utf8mb4"
            async_session_factory = sessionmaker(class_=AsyncSession, bind=create_async_engine(ASYNCDBURL, echo=True))
            AsyncSession = async_scoped_session(async_session_factory, scopefunc=asyncio.current_task)#type: ignore
            async with AsyncSession() as db:

                while 1:
                    order=await Service.orderService.findByPk(db,order_id)
                    order.market_name=str(random.randint(100,2000))
                    await asyncio.sleep(0.1)
                    await db.commit()
        loop=asyncio.new_event_loop()
        loop.run_until_complete(updateorder(61821984346146))

    #th=[threading.Thread(target=testupdatefailed) for i in range(10)]
    th = [threading.Thread(target=testupdatefailedretry) for i in range(10)]
    for t in th:
        t.start()
    for t in th:
        t.join()
if __name__ == "__main__":
    test()


