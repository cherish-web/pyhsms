# _*_ coding: utf-8 _*_
#@Time      : 2020/7/29 上午 09:49
#@Author    : cherish_peng
#@Email     : 1058386071@qq.com
#@File      : messagetype.py
#@Software  : PyCharm
from enum import Enum
class MessageType(Enum):
    '''
    MessageType enum
    '''
    DataMessage       = 0b0000_0000
    SelectRequest     = 0b0000_0001
    SelectResponse    = 0b0000_0010
    #Deselect_req      = 0b0000_0011
    #Deselect_rsp      = 0b0000_0100
    LinkTestRequest   = 0b0000_0101
    LinkTestResponse  = 0b0000_0110
    #Reject_req        = 0b0000_0111
    SeperateRequest   = 0b0000_1001