import os
import random

from typing import Any, List, Literal
import aiosmtplib
import settings
from common.CommonError import ResponseException

from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart

from component.cache import cache


class MailService():
    async def sendMail(self, from_email: str = '', to_email: List[str] = None, subject: str = '', content: str = '',
                       contextType: Literal['plain', 'html'] = 'plain') -> None:
        if not from_email:
            from_email = os.environ.get('SYSTEM_MAIL_USER')  # type: ignore
        if not to_email:
            raise ResponseException({'status': 'failed', 'errormsg': 'to_email is required'})
        msg = MIMEMultipart()
        msg.preamble = subject
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = ','.join(to_email)
        print('to:', to_email)
        print('from:', from_email)
        msg.attach(MIMEText(content, contextType, 'utf-8'))

        smtp = aiosmtplib.SMTP(os.environ.get('SYSTEM_MAIL_SERVER'),  # type: ignore
                               port=os.environ.get('SYSTEM_MAIL_OUTPORT'),  # type: ignore
                               use_tls=True)  # type: ignore
        await smtp.connect()
        await smtp.login(os.environ.get('SYSTEM_MAIL_USER'), os.environ.get('SYSTEM_MAIL_PASSWORD'))  # type: ignore

        try:
            await smtp.send_message(msg)
            await smtp.quit()
        except Exception as e:

            print(e)
            raise ResponseException({'status': 'failed', 'errormsg': 'send email failed'})

    async def sendMerchantRegisterVerifyMail(self, to_email: str) -> Any:

        verifycode = random.randint(100000, 999999)
        await cache.set(f'MerchantRegisterverifycode:{to_email}', verifycode, 1800)
        subject = "xtopus verify code"
        content = f"your verify code is {verifycode}"
        await self.sendMail(os.environ.get('SYSTEM_MAIL_USER'), [to_email], subject, content)  # type: ignore

    async def verifyMerchantRegisterVerifyMailCode(self, email_address: str, incode: str) -> bool:
        code = await cache.get(f'MerchantRegisterverifycode:{email_address}')
        if not code:
            return False
        if int(code) != int(incode):
            return False
        return True

    async def sendNewMerchantApply(self, email_address: str, merchant_name: str,
                                   company_name: str) -> Any:
        subject = "new merchant apply"
        content = f"{merchant_name} apply to be a xtopus merchant"
        await self.sendMail(os.environ.get('SYSTEM_MAIL_USER'), [email_address], subject, content)  # type: ignore


if __name__ == '__main__':
    import Service
    from common.globalFunctions import cmdlineApp


    @cmdlineApp
    async def test(db) -> Any:  # type: ignore
        await Service.mailService.sendMerchantRegisterVerifyMail('1299693999@qq.com')


    test()
