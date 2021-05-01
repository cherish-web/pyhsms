# _*_ coding: utf-8 _*_
#@Time      : 2020/7/29 上午 09:49
#@Author    : cherish_peng
#@Email     : 1058386071@qq.com
#@File      : secsformat.py
#@Software  : PyCharm
from enum import Enum
class SecsFormat(Enum):
    '''
    SecsFormat Enum
    '''
    List = 0b0000_00_00
    Binary = 0b0010_00_00
    Boolean = 0b0010_01_00
    ASCII = 0b0100_00_00
    JIS8 = 0b0100_01_00
    I8 = 0b0110_00_00
    I1 = 0b0110_01_00
    I2 = 0b0110_10_00
    I4 = 0b0111_00_00
    F8 = 0b1000_00_00
    F4 = 0b1001_00_00
    U8 = 0b1010_00_00
    U1 = 0b1010_01_00
    U2 = 0b1010_10_00
    U4 = 0b1011_00_00
    def __str__(self):
        if self.name == 'List':
            return 'L'
        if self.name == 'Binary':
            return 'B'
        if self.name == 'ASCII':
            return 'A'
        return self.name
    def getattr(attr):
        if attr == 'L':
            return SecsFormat.List
        if attr == 'B':
            return SecsFormat.Binary
        if attr == 'A':
            return SecsFormat.ASCII
        if attr in SecsFormat.__members__:
            return SecsFormat.__getattribute__(SecsFormat,attr)
        raise Exception("'SecsFormat has'nt attr:"+attr)
#print('List' in SecsFormat.__members__)
#print(SecsFormat.getattr('L'))
#print('L'==str(SecsFormat.List))