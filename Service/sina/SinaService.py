import datetime

import aiohttp
import orjson

import settings


class SinaService():
    async def get(self,url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:

                text=await resp.text()
                return text
    async def getHistoryDayData(self, code, start_date, end_date, datatime=None):

        url=f'https://q.stock.sohu.com/hisHq?code=cn_{code}&start={start_date}&end={end_date}'
        print('url;',url)
        ret=await self.get(url)
        data=orjson.loads(ret)
        print('data:',data)
        arr=[]
        for i in data[0]['hq']:#datetime.datetime.strptime(i[0],'%Y-%m-%d').timestamp()*1000
            arr.append([i[0],float(i[1]),float(i[6]),float(i[5]),float(i[2])])
        return arr

