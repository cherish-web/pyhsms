# _*_ coding: utf-8 _*_
#@Time      : 2020/7/29 上午 10:15
#@Author    : cherish_peng
#@Email     : 1058386071@qq.com
#@File      : item.py
#@Software  : PyCharm
import sys
import json
from .secsformat import SecsFormat
import struct
class Item:
    '''secs meaasge body's item'''
    def __init__(self, format :SecsFormat, value=[]):
        self.format = format
        if isinstance(value, (list, str, bytes, bytearray)):
            self.value = value
        else:
            '''
            if self.format in (SecsFormat.Binary, SecsFormat.Boolean):
                self.value = bytearray((value,))
            else:
            '''
            self.value = []
            self.value.append(value)
        if format in (SecsFormat.I1, SecsFormat.I2, SecsFormat.I4, SecsFormat.I8,
                      SecsFormat.U1, SecsFormat.U2, SecsFormat.U4, SecsFormat.U8):
            self.value = list(map(lambda x: self.checkvalue(format, x), self.value))
        self.items = []
        if format == SecsFormat.List and value:
            self.items = value

    def checkvalue(self, format, value):
        valuebitlength = int(str(format)[-1:]) * 8
        umax_value = 0xffffffffffffffff >> (64 - valuebitlength)
        if format in (SecsFormat.I1, SecsFormat.I2, SecsFormat.I4, SecsFormat.I8):
            max_value = umax_value >> 1
            if value > max_value:
                return max_value
            if value < -max_value-1:
                return -max_value-1
            return value
        if value < 0:
            return 0
        if value > umax_value:
            return umax_value
        return value

    def getvaluelenth(self):
        '''
        return item count
        :return: int
        '''
        if self.format == SecsFormat.List:
            return len(self.items)
        return len(self.value)

    def additem(self,item):
        '''
        add subitem
        :param item: Item
        :return: Item
        '''
        if self.format != SecsFormat.List:
            raise Exception(str.format("format({0}) can't add item", self.format))

        if isinstance(item,list):
            for itm in item:
                self.items.append(itm)
        else:
            self.items.append(item)
        if len(self.items) > 255:
            raise Exception(str.format("List items length({0}) out of range, max length: 255", len(self.items)))
        return self

    def tosml(self):
        '''
        Item to sml format string
        :return: str
        '''
        return Item.itemtosml(self)+'.'
    def tojson(self,key:str):
        '''
        Item to json format string
        :param key: 键值
        :return: str
        '''
        print(Item.itemtolist(self))
        return json.dumps({key:Item.itemtolist(self)})

    @staticmethod
    def jsontoitem(str):
        '''
        json format string to Item
        :return: Item
        '''
        dic = json.loads(str)
        return Item.dictoitem(dic)

    @staticmethod
    def dictoitem(dic):
        '''
        dic to Item
        :return: Item
        '''
        for key in dic:
            return Item.listtoitem(dic[key])
        raise Exception("dic convert item errpr,dic can't null")

    @staticmethod
    def dictoitems(dic):
        '''
        dic to Items
        :return:
        '''
        items = []
        for key in dic:
            items.append(Item.listtoitem(dic[key]))
        return items

    @staticmethod
    def jsontoitems(str):
        '''
        json format string to Items
        :return:
        '''
        items=[]
        dic = json.loads(str)
        return Item.dictoitems(dic)

    @staticmethod
    def itemtosml(item, smlstr='', count=0):
        '''
        Item to sml format string
        :param item: Item
        :param smlstr: default
        :param count: default
        :return: str
        '''
        enter = '\n'
        if not count:
            enter = ''
        if item.format == SecsFormat.List:
            if item.items:

                smlstr += enter + str.format(' '*count+'<{0}[{1}]', str(item.format), len(item.items))
                for it in item.items:
                    smlstr = Item.itemtosml(item=it, smlstr=smlstr, count=count+4)

                return smlstr + '\n' + ' ' * count + '>'
            else:
                return smlstr+enter+str.format(' '*count+'<{0}[{1}]>', str(item.format), len(item.items))
        if item.format == SecsFormat.Binary:
            value = item.value
            if isinstance(item.value, (list, bytes, bytearray)):
                if len(item.value) > 9:
                    value = ''
                    maxvalue = len(item.value)
                    if maxvalue % 10:
                        maxvalue = maxvalue//10+1
                    else:
                        maxvalue = maxvalue // 10
                    for index in range(0, maxvalue):
                        value += '\n'+' ' * (count+4) + ' '.join(list(map(lambda x:hex(x) if x>15 else hex(x)+' ', list(item.value[index*10:index*10+10]))))
                    return smlstr + enter + str.format(' ' * count + '<{0}[{1}]' + '{2}\n' +
                                                       ' ' * count + '>', str(item.format), len(item.value),
                                                       value)
            return smlstr + enter + str.format(' '*count+'<{0}[{1}] {2}>', str(item.format), len(item.value),
                                               ' '.join(list(map(lambda x: hex(x), item.value))))
        if item.format == SecsFormat.ASCII:
            return smlstr + enter + str.format(' ' * count + "<{0}[{1}] '{2}'>", str(item.format), item.value.__len__(), item.value)
        if item.format == SecsFormat.Boolean:
            return smlstr + enter + str.format(' '*count+'<{0}[{1}] {2}>', str(item.format), len(item.value),
                                               ' '.join(list(map(lambda x: hex(x), item.value))))
        if isinstance(item.format, SecsFormat):
            return smlstr + enter + str.format(' '*count+'<{0}[{1}] {2}>', str(item.format), len(item.value),
                                               ' '.join(list(map(lambda x: str(x), item.value))))
        raise Exception('invalid SecsFormat value')

    @staticmethod
    def itemtolist(item):
        '''
        Item to list
        :param item: Item
        :return: list
        '''
        sublist = []
        if item.format == SecsFormat.List:
            if item.items:
                for it in item.items:
                    if it.format == SecsFormat.List:
                        sublist.append(Item.itemtolist(item=it))
                    else:
                        sublist+=(Item.itemtolist(item=it))
                return sublist
            else:
                return []
        if isinstance(item.format, SecsFormat):
            return [{str(item.format):item.value}]
        raise Exception('invalid SecsFormat value')

    @staticmethod
    def listtoitem(datalist:list):
        '''
        list to Item
        :return: Item
        '''
        item = Item(SecsFormat.List)
        for data in datalist:
            if isinstance(data,dict):
                for key in data:
                    if key in (str(SecsFormat.Binary),str(SecsFormat.Boolean)):
                        item.additem(Item(SecsFormat.getattr(attr=key), list(map(lambda x:int(x,16),data[key].split(' ')))))
                    elif key in (str(SecsFormat.U1),str(SecsFormat.U2),str(SecsFormat.U4),str(SecsFormat.U8),
                               str(SecsFormat.I1),str(SecsFormat.I2),str(SecsFormat.I4),str(SecsFormat.I8)):
                        item.additem(Item(SecsFormat.getattr(attr=key), list(map(lambda x:int(x),data[key].split(' ')))))
                    elif key in (str(SecsFormat.F4),str(SecsFormat.F8)):
                        item.additem(Item(SecsFormat.getattr(attr=key), list(map(lambda x:float(x),data[key].split(' ')))))
                    else:
                        item.additem(Item(SecsFormat.getattr(attr=key),data[key]))
            if isinstance(data, list):
                item.additem(Item.listtoitem(data))
        return item

    @staticmethod
    def decode(btarray:bytes):
        '''
        bytes to Item
        :param btarray: bytes
        :return: Item
        '''
        def dec(btarray:bytes, index=0):
            '''
            bytes to Item
            :param btarray: bytes
            :param index: default
            :return: Item,int
            '''

            format = (SecsFormat)(btarray[index] & 0xFC)
            if not isinstance(format, SecsFormat):
                raise Exception(str.format("bytes of format({0})  can't decode", format))
            lengthbits = btarray[index] & 3
            index += 1
            itemlengthbytes = btarray[index:index+lengthbits]
            datalength = int.from_bytes(bytes=itemlengthbytes, byteorder='big', signed=False)
            index += lengthbits
            if format == SecsFormat.List:
                if not datalength:
                    return Item(SecsFormat.List), index
                items = []
                for i in range(datalength):
                    item, index = dec(btarray, index)
                    if item:
                        items.append(item)
                return Item(SecsFormat.List, items), index
            bts = btarray[index:index + datalength]
            index += datalength
            item = []
            if format in (SecsFormat.ASCII, SecsFormat.JIS8):
                item = Item(format, bts.decode())
            elif format in (SecsFormat.Binary, SecsFormat.Boolean):
                item = Item(format, bts)
            elif format == SecsFormat.F4:
                item = Item(format, list(map(lambda x: round(x, 5), struct.unpack(str.format('!{0}f', datalength//4), bts))))
            elif format == SecsFormat.F8:
                item = Item(format, list(map(lambda x: round(x, 5), struct.unpack(str.format('!{0}d', datalength//8), bts))))
            else:
                value = []
                btslength = int(str(format)[-1:])
                length = datalength // btslength
                for i in range(length):
                    if format in (SecsFormat.U1, SecsFormat.U2, SecsFormat.U4, SecsFormat.U8):
                        value.append(int.from_bytes(bytes=bts[i*btslength:i*btslength+btslength], byteorder='big', signed=False))
                    elif format in (SecsFormat.I1, SecsFormat.I2, SecsFormat.I4, SecsFormat.I8):
                        value.append(int.from_bytes(bytes=bts[i*btslength:i*btslength+btslength], byteorder='big', signed=True))
                    item = Item(format, value)
            return item, index

        item, _ = dec(btarray)
        return item
    def encode(self):
        bts=bytearray()
        labts = bytearray(1)
        if not isinstance(self.format, SecsFormat):
            raise Exception(str.format("Item of format({0})  can't encode", self.format))
        def getitemlengthbts():
            itemlength=0
            if self.format == SecsFormat.List:
                itemlength = len(self.items)
            elif self.format in (SecsFormat.ASCII, SecsFormat.JIS8, SecsFormat.Boolean, SecsFormat.Binary):
                itemlength = len(self.value)
            else:
                for val in self.value:
                    itemlength += int(str(self.format)[-1:])
            if itemlength >> 24:
                raise Exception(str.format("Item data length:{0} is overflow",itemlength))
            if itemlength >> 16:
                return bytearray(itemlength.to_bytes(length=3, byteorder='big', signed=True))
            if itemlength >> 8:
                return bytearray(itemlength.to_bytes(length=2, byteorder='big', signed=True))
            return bytearray((itemlength,))
        itemlengthbts = getitemlengthbts()
        bts += bytearray((self.format.value | len(itemlengthbts),)) + itemlengthbts
        if self.format == SecsFormat.List:
            for item in self.items:
                bts += item.encode()
            return bts
        if self.format in (SecsFormat.ASCII, SecsFormat.JIS8):
            return bts + self.value.encode('utf-8')
        if self.format in (SecsFormat.Binary, SecsFormat.Boolean):
            return bts + bytearray(tuple(self.value))
        for val in self.value:
            if self.format == SecsFormat.F4:
                    bts += struct.pack('!f', val)
            elif self.format == SecsFormat.F8:
                    bts += struct.pack('!d', val)
            elif self.format in (SecsFormat.I1, SecsFormat.U1):
                if val < 0:
                    bts += bytearray(((val + 256) & 0xff,))
                else:
                    bts += bytearray((val,))
            else:
                length = int(str(self.format)[-1:])
                if self.format in (SecsFormat.U2, SecsFormat.U4, SecsFormat.U8):
                    bts += val.to_bytes(length=length, byteorder='big', signed=False)
                elif self.format in (SecsFormat.I2, SecsFormat.I4, SecsFormat.I8):
                    bts += val.to_bytes(length=length, byteorder='big', signed=True)
        return bts


if __name__ =="__main__":
    '''
    <L[9]
        <A[5] 'hello'>
        <F4[2] 1.235 2223.55005>
        <L[5]
            <F8[1] 2.235>
            <I1[2] -1 44>
            <I2[2] 333 456>
            <I4[2] 99889 -66844>
            <I8[2] 998899999 6856844>
        >
        <U1[2] 55 255>
        <U2[1] 5563>
        <U4[2] 99889 6856844>
        <U8[1] 911922999>
        <Boolean[2] 0x1 0x2>
        <B[3] 0x1 0xff 0x3>
    >.
    '''
    #method1
    item = Item(SecsFormat.List)
    item1 = Item(SecsFormat.ASCII, 'hello')
    item2 = Item(SecsFormat.F4, [1.235, 2223.55])
    item3 = Item(SecsFormat.F8, 2.235)
    item4 = Item(SecsFormat.I1, [-1, 44])
    item5 = Item(SecsFormat.I2, [333, 456])
    item6 = Item(SecsFormat.I4, [99889, -66844])
    item7 = Item(SecsFormat.I8, [998899999, 6856844])
    item8 = Item(SecsFormat.U1, [55, 255])
    item9 = Item(SecsFormat.U2, 5563)
    item10 = Item(SecsFormat.U4, [99889, 6856844])
    item11 = Item(SecsFormat.U8, 911922999)
    item12 = Item(SecsFormat.Boolean, [0x01, 0x02])
    item13 = Item(SecsFormat.Binary, [0x01, 0xff, 0x03])
    item = Item(SecsFormat.List, [
        item1,
        item2,
        Item(SecsFormat.List, [
            item3,
            item4,
            item5,
            item6,
            item7
        ]),
        item8,
        item9,
        item10,
        item11,
        item12,
        item13
    ])
    # method2
    item4 = Item(SecsFormat.List,
                [
                    Item(SecsFormat.ASCII, 'hello'),
                    Item(SecsFormat.F4, [1.235, 2223.55]),
                    Item(SecsFormat.List,
                         [
                             Item(SecsFormat.F8, 2.235),
                             Item(SecsFormat.I1, [-1, 44]),
                             Item(SecsFormat.I2, [333, 456]),
                             Item(SecsFormat.I4, [99889, -66844]),
                             Item(SecsFormat.I8, [998899999, 6856844]),
                         ]),
                    Item(SecsFormat.U1, [55, 255]),
                    Item(SecsFormat.U2, 5563),
                    Item(SecsFormat.U4, [99889, 6856844]),
                    Item(SecsFormat.U8, 911922999),
                    Item(SecsFormat.Boolean, [0x01, 0x02]),
                    Item(SecsFormat.Binary, bytes((0x01, 0xff, 0x03))),
                ])
    print(item.tosml())
    print(item.encode())
    it = Item.decode(item.encode())
    print(it.tosml())


        