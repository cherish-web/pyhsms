# _*_ coding: utf-8 _*_
#@Time      : 2020/7/29 上午 10:59
#@Author    : cherish_peng
#@Email     : 1058386071@qq.com
#@File      : systembytegenerator.py
#@Software  : PyCharm
#from uuid import *
import uuid
import threading
class SystemByteGenerator:
    UUID = uuid.uuid1().__hash__()&0xffffffff
    lock = threading.Lock()
    @staticmethod
    def generator():
        '''
        generate token
        :return: int
        '''
        SystemByteGenerator.lock.acquire()
        SystemByteGenerator.UUID+= 1
        SystemByteGenerator.lock.release()
        return SystemByteGenerator.UUID