# _*_ coding: utf-8 _*_
#@Time      : 2020/7/29 上午 09:49
#@Author    : cherish_peng
#@Email     : 1058386071@qq.com
#@File      : header.py
#@Software  : PyCharm
from .messagetype import MessageType
from .systembytegenerator import SystemByteGenerator
class MessageHeader:

    '''
    secs meassage header
    '''
    def __init__(self,deviceid:int,replyexpected:bool,msgtype:MessageType,systembyte,s=0,f=0):
        '''
        :param deviceid: int
        :param replyexpected: bool
        :param messagetype: MessageType
        :param systembytes: int
        :param s: int
        :param f: int
        '''
        self.deviceid=deviceid
        self.replyexpected=replyexpected
        self.s=s
        self.f=f
        self.msgtype=msgtype
        self.systembyte=systembyte
    def toencode(self):
        '''
        MessageHeader to bytes
        :return: bytearray
        '''
        head = bytearray(6)
        head[0] =self.deviceid&0xff
        head[1] = self.deviceid>>8 & 0xff
        head[2]=self.s|self.replyexpected<<7
        head[3]=self.f
        head[4]=0
        head[5]=self.msgtype.value
        head += self.systembyte.to_bytes(length=4,byteorder='big',signed=False)
        return head
    @staticmethod
    def decode(data:bytearray):
        '''
        bytes to MessageHeader
        :param data:
        :return:
        '''
        head = data
        s = head[2]
        deviceid = int.from_bytes(bytes=head[0:2],byteorder='big',signed=False)
        replyexpected= bool(s & 0b1000_0000)
        s = s & 0b0111_111
        f = int(head[3])
        msgtype=MessageType(head[5])
        systembyte = int.from_bytes(head[6:10], byteorder='big', signed=False)
        return MessageHeader(deviceid=deviceid,replyexpected=replyexpected,s=s,f=f,msgtype=msgtype,systembyte=systembyte)