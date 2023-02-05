import aiohttp

import settings


class TuShareService():
    def __init__(self):
        pass
    async def post(self,indata=None):
        pass
        data={
            "api_name":"stock_basic",
            "token":settings.tusharetoken,
            "params":{"list_status":"L"},
            "fields":""
        }
        if indata:
            data.update(indata)
        async with aiohttp.ClientSession() as session:
            async with session.post("http://api.tushare.pro",json=data) as resp:
                return await resp.json()

    async def getBasicInfo(self):
        ret=await self.post()
        print(ret)

if __name__ == "__main__":
    pass

    from common.globalFunctions import cmdlineApp
    @cmdlineApp
    async def test(db):
        service = TuShareService()
        ret=await service.getBasicInfo()
    test()