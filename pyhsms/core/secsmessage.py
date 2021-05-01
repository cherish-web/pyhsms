# _*_ coding: utf-8 _*_
#@Time      : 2020/7/29 上午 10:04
#@Author    : cherish_peng
#@Email     : 1058386071@qq.com
#@File      : secsmessage.py
#@Software  : PyCharm
from .messagetype import MessageType
from .header import MessageHeader
from .item import Item
from .secsformat import SecsFormat
from .systembytegenerator import SystemByteGenerator
class SecsMessage:

    def __str__(self):
        replyStr =''
        if self.replyexpected:
            replyStr = 'W'
        return str.format("S{0}F{1} {2} Name:{3}",int(self.s),int(self.f),replyStr,self.name)

    def __init__(self,item = None, name=None, msgtype=None,s=0,f=0, replyexpected = False, deviceid = 0xffff,systembyte=None):
        if s > 0b0111_1111:
            raise Exception('stream number must less than 127')
        self.s = s
        self.f = f
        self.name = name
        self.replyexpected = replyexpected
        self.secsitem = item
        if isinstance(systembyte,int):
            self.systembyte = systembyte
        else:
            self.systembyte = SystemByteGenerator.generator()
        self.deviceid = deviceid
        self.msgtype = MessageType.DataMessage
        if msgtype:
            self.msgtype = msgtype

    def get_itemvaluebyindex(self,index):
        def get_itemvalue(items:Item,deep=0):
            if items.format == SecsFormat.List:
                deep += 1
                value = None
                if index == deep:
                    return value,deep
                for item in items.items:
                    value,deep = get_itemvalue(item,deep)
                    if index == deep:
                        return value,deep
                return value,deep
            deep +=1
            if index == deep:
                if items.format in (SecsFormat.Binary, SecsFormat.Boolean):
                    return ' '.join(list(map(lambda x:hex(x),items.value))), deep
                return items.value,deep
            return None,deep
        value,num = get_itemvalue(self.secsitem)
        if index<1 or index>num:
            raise Exception("Func:get_itemvaluebyindex exec err, Index({0}) out of bounds(1~{1})".format(index,num))
        if isinstance(value,(list,tuple)):
            if value:
                return value[0]
        return value

    def set_itemvaluebyindex(self,index,value):
        def set_itemvalue(items:Item,deep=0):
            if items.format == SecsFormat.List:
                deep += 1
                if index == deep:
                    items.value = self.formatvalue(items.format,value)
                    return deep
                for item in items.items:
                    deep = set_itemvalue(item,deep)
                    if index == deep:
                        items.value = self.formatvalue(items.format,value)
                        return deep
                return deep
            deep +=1
            if index == deep:
                items.value = self.formatvalue(items.format,value)
            return deep
        num = set_itemvalue(self.secsitem)
        if index < 1 or index > num:
            raise Exception("Func:set_itemvaluebyindex exec err, Index({0}) out of bounds(1~{1})".format(index, num))

    def formatvalue(self,format:SecsFormat,value):
        if format in (SecsFormat.ASCII,SecsFormat.JIS8):
            value = str(value)
        elif format in (SecsFormat.I1, SecsFormat.I2, SecsFormat.I4, SecsFormat.I8,
                              SecsFormat.U1, SecsFormat.U2, SecsFormat.U4, SecsFormat.U8):
            if isinstance(value, (list)):
                value = list(map(lambda x:int(x),value))
            else:
                value = int(value)
        elif format in (SecsFormat.F4, SecsFormat.F8):
            if isinstance(value, (list)):
                value = list(map(lambda x:round(float(x),5),value))
            else:
                value = round(float(value), 5)
        elif format in (SecsFormat.Binary, SecsFormat.Boolean):
            if isinstance(value, (list)):
                value = list(map(lambda x:int(x)&0xff,value))
            else:
                value = int(value)&0xff
        else:
            raise Exception("the item format({0}) err, can't set value".format(format))
        return value

    def encode(self, msgtype=None, systembyte=None):
        '''
        SecsMessage to bytes
        :param msgtype: MessageType, default = MessageType.DataMessage
        :param systembyte: int, default = None
        :return: bytearray
        '''
        if not systembyte:
            systembyte = self.systembyte
        if not msgtype:
            msgtype = self.msgtype
        if msgtype == MessageType.DataMessage:
            head = MessageHeader(deviceid=self.deviceid, replyexpected=self.replyexpected,
                                 msgtype=msgtype, systembyte=systembyte, s=self.s, f=self.f)
            headbts = head.toencode()
            itembts = bytearray()
            if isinstance(self.secsitem, Item):
                itembts = self.secsitem.encode()
            messagelength = len(headbts)+len(itembts)
            messagelengthbts = messagelength.to_bytes(length=4, byteorder='big', signed=True)

            return messagelengthbts + headbts + itembts
        if isinstance(msgtype, MessageType):
            bts = bytearray(4)
            bts[3] = 10
            head = MessageHeader(self.deviceid, self.replyexpected, msgtype, systembyte)
            bts += head.toencode()
            return bts
        raise Exception("class MessageType has't type:", msgtype)

    def gethead(self):
        head = MessageHeader(deviceid=self.deviceid, replyexpected=self.replyexpected,
                      msgtype=self.msgtype, systembyte=self.systembyte, s=self.s, f=self.f)
        return head

    @staticmethod
    def decode(btsayyay:bytearray):
        '''
        bytes to SecsMessage
        :param btarray: bytes
        :return: SecsMessage||None
        '''
        if len(btsayyay) < 10:
            return
        head = MessageHeader.decode(btsayyay)

        if head.msgtype == MessageType.DataMessage and len(btsayyay) > 10:
            item = Item.decode(btsayyay[10:])
            return SecsMessage(item=item, s=head.s, f=head.f,
                               replyexpected=head.replyexpected, deviceid=head.deviceid,systembyte=head.systembyte)
        msg = SecsMessage(s=head.s, f=head.f, replyexpected=head.replyexpected, deviceid=head.deviceid,systembyte=head.systembyte)
        msg.msgtype = head.msgtype
        return msg

    def tosml(self):
        if self.secsitem:
            return self.secsitem.tosml()
        return self.encode()
