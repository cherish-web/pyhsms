# _*_ coding: utf-8 _*_
#@Time      : 2020/7/29 上午 11:20
#@Author    : cherish_peng
#@Email     : 1058386071@qq.com
#@File      : streamdecoder.py
#@Software  : PyCharm
from .header import MessageHeader
from .messagetype import MessageType
from .secsmessage import SecsMessage

class Streamdecoder:
    BUFFER = bytearray()

    @staticmethod
    def decode(btarray:bytearray):
        '''
        bytes to SecsMessage list
        :param btarray: bytes
        :return: list(SecsMessage)
        '''
        Streamdecoder.BUFFER += btarray
        #count = 0
        def dec(btsarray: bytearray, index=0):
            #nonlocal count
            #count +=1
            secsmsglist = []
            if len(btsarray) < 14:
                return secsmsglist, index
            bts = btsarray[0:4]
            messagedatalength = int.from_bytes(bytes=bts, byteorder='big', signed=False)
            #print("Get Message Length:", messagedatalength)
            bts = btsarray[4:]
            if len(bts) > messagedatalength - 1:
                msg = SecsMessage.decode(bts)
                if msg:
                    secsmsglist.append(msg)
                    msglist,index =dec(btsarray=btsarray[messagedatalength+4:], index=index + messagedatalength + 4)
                    secsmsglist +=msglist
            return secsmsglist,index
        #print('count:',count)
        secsmsglist, index = dec(btsarray=Streamdecoder.BUFFER)
        Streamdecoder.BUFFER = Streamdecoder.BUFFER[index:]
        return secsmsglist


