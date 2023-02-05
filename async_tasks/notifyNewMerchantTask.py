import time

import orjson

from component.cache import cache

if __name__ == '__main__':
    import sys
    from pathlib import Path

    sys.path.insert(0, Path(__file__).parent.parent.__str__())

from sqlalchemy.ext.asyncio import AsyncSession

import Service
from celery_app import celery_app
import datetime

from common.globalFunctions import cmdlineApp
from sqlalchemy import update
import Models
from component.dbsession import getdbsession


@celery_app.task
@cmdlineApp
async def notifyNewMerchant(db: AsyncSession, merchant_id: int) -> None:  # type: ignore
    # 所有有通知权限的角色
    merchant = await Service.merchantService.findByPk(db, merchant_id)
    if not merchant:
        return None
    models = await Service.graphpermissionService.find(db, {'notify_columns': 'Y'})
    # 所有用户
    users = await Service.userService.find(db, {'userrole__in': [model.role_id for model in models]})
    for user in users:
        if user.email:
            try:
                # 邮件通知
                await Service.mailService.sendNewMerchantApply(user.email, merchant.merchant_name,
                                                               merchant.company_name)

                # 站内实时消息通知
                msg = f"{merchant.merchant_name} apply to be a xtopus merchant"
                content = {"cmd": 'notify', 'msg': msg, 'gotoroute': "system.merchant.newapply", 'params': merchant_id}
                await cache.rPush(f'ttlmsg:{user.user_id}', orjson.dumps(content), 3600 * 3)
            except Exception as e:
                print(e)
                pass
