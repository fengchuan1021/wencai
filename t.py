import base64
import re

Authorization='Basic YWRtaW46cGFzc3dvcmQx'

a=base64.b64decode(Authorization.split(' ')[1])
print(a)