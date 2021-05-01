# _*_ coding: utf-8 _*_
#@Time      : 2020/8/13 上午 11:50
#@Author    : cherish_peng
#@Email     : 1058386071@qq.com
#@File      : errsecsmsg.py
#@Software  : PyCharm
import sys,os

from .item import Item
from .secsmessage import SecsMessage
from .header import MessageHeader
from .messagetype import MessageType
from .secsformat import SecsFormat
from enum import Enum
import re

class ErrSecsMsgType(Enum):
    DeviceidErr=1
    StreamErr = 3
    FounctionErr = 5
    IllegalData = 7
    TransactionTimerTimeout = 9
    ConversationTimeout = 13
    ErrSecsMsgReply = 0
class ErrSecsMsg:
    NORMMSGLIST=[]
    DEVICEID = 0
    @classmethod
    def get_errmsg(cls,errmsgtype:ErrSecsMsgType,msg:SecsMessage):
        item = Item(SecsFormat.Binary,msg.gethead().toencode())
        msg =SecsMessage(s=9,f=errmsgtype.value,item=item,msgtype=MessageType.DataMessage,
                         deviceid=cls.DEVICEID,systembyte=msg.systembyte)
        return msg

    @classmethod
    def iserrmsg(cls,msg:SecsMessage):
        if msg.s == 9:
            if msg.f in (1,3,5,7,9,13):
                return ErrSecsMsgType.ErrSecsMsgReply
            return ErrSecsMsgType.IllegalData
        if msg.deviceid != cls.DEVICEID:
            return ErrSecsMsgType.DeviceidErr
        if str.format('S{0}F{1}',msg.s,msg.f) not in cls.NORMMSGLIST:
            if msg.s in list(map(lambda x:cls.gets(x) ,cls.NORMMSGLIST)):
                return ErrSecsMsgType.FounctionErr
            return ErrSecsMsgType.StreamErr

    @classmethod
    def gets(cls,x):
        result = re.match(r'^s(.*?)f',x)
        if result:
            return int(result.groups()[0])
        return None

    @classmethod
    def init_ErrSecsMsg(cls,normsglist=None,deviceid=None):
        if isinstance(deviceid,int):
            cls.DEVICEID = deviceid
        if isinstance(normsglist,list):
            cls.NORMMSGLIST = normsglist
