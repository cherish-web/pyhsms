# _*_ coding: utf-8 _*_
#@Time      : 2020/7/29 上午 09:49
#@Author    : cherish_peng
#@Email     : 1058386071@qq.com
#@File      : connectionstate.py
#@Software  : PyCharm
from enum import Enum
class ConnectionState(Enum):
    '''
    ConnectionState enum
    '''
    DisConnected = 0
    Connecting=1
    Connected=2
    Selected=3
    Retry=4