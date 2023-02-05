import asyncio
import Models
from component.dbsession import getdbsession
import Service
from component.snowFlakeId import snowFlack


async def adddefaultadmin() -> None:
    async with getdbsession() as dbclient:
        try:
            db = dbclient.session
            root = Models.User(username='root', password=Service.userService.get_password_hash('root'),
                               user_id=snowFlack.getId(), role_id=1)
            merchant = Models.User(username='merchant', password=Service.userService.get_password_hash('merchant'),
                                   user_id=snowFlack.getId(), role_id=2)

            db.add(root)

            rootrole = Models.UserRole(user_role_id=1, role_name='super admin', merchant_id=0, mark='dont delete this')
            db.add(rootrole)
            merchantrole = Models.UserRole(user_role_id=2, role_name='main merchant', merchant_id=0,
                                           mark='dont delete this')

            merchantModel = Models.Merchant(user_id=merchant.user_id, merchant_name='unineed',
                                            merchant_id=snowFlack.getId())
            db.add(merchantModel)
            merchant.merchant_id = merchantModel.merchant_id
            db.add(merchant)
            db.add(merchantrole)
            await db.flush()

            # await Service.userService.create(db, merchant)  # type: ignore
            # role=await Service.roleService.create(db,{"role_name":"root",'note':"super user"})
            # merchantrole = await Service.roleService.create(db, {"role_name": "merchant", 'note': "merchant user"})
            await db.commit()
        except Exception as e:
            print(e)
            await db.rollback()


def addroot() -> None:
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(adddefaultadmin())


if __name__ == '__main__':
    asyncio.run(adddefaultadmin())
