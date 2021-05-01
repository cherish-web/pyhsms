# _*_ coding: utf-8 _*_
#@Time      : 2020/8/25 上午 10:31
#@Author    : cherish_peng
#@Email     : 1058386071@qq.com
#@File      : logger.py
#@Software  : PyCharm
#! /usr/bin/env python
#coding=gbk
import logging
import ctypes
import threading
import platform

if platform.system() == 'Windows':
    FOREGROUND_WHITE = 0x0007
    FOREGROUND_BLUE = 0x01  # text color contains blue.
    FOREGROUND_GREEN = 0x02  # text color contains green.
    FOREGROUND_RED = 0x04  # text color contains red.
    FOREGROUND_YELLOW = FOREGROUND_RED | FOREGROUND_GREEN

    STD_OUTPUT_HANDLE = -11
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    def set_color(color, handle=std_out_handle):
        bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        return bool
else:
    FOREGROUND_WHITE = '\033[0m'
    FOREGROUND_BLUE = '\033[0;34;40m' # text color contains blue.
    FOREGROUND_GREEN= '\033[0;32;40m' # text color contains green.
    FOREGROUND_RED  = '\033[0;31;40m' # text color contains red.
    FOREGROUND_YELLOW = '\033[0;33;40m'


class Logger:
    gvloger = None
    def __init__(self, c_level=logging.DEBUG,path='', f_level = logging.DEBUG):
        if Logger.gvloger:
            raise Exception("Logger can only be instantiated")
        self.logger = logging.getLogger(path)
        self.logger.setLevel(logging.DEBUG)
        self.lock = threading.Lock()
        #fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        #设置CMD日志
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        sh.setLevel(c_level)
        self.logger.addHandler(sh)
        #设置文件日志
        if path:
            fh = logging.FileHandler(path, encoding='utf-8')
            fh.setFormatter(fmt)
            fh.setLevel(f_level)
            self.logger.addHandler(fh)
        Logger.gvloger = self

    @classmethod
    def getlogger(cls):
        if not cls.gvloger:
            cls.gvloger = Logger()
        return cls.gvloger

    def debug(self,message):
        self.logger.debug(message)

    def setcolor(self,func,message,color):
        if platform.system() == 'Windows':
            set_color(color)
            func(message)
            set_color(FOREGROUND_WHITE)
        else:
            func(color+message+FOREGROUND_WHITE)

    def info(self,message,color=FOREGROUND_GREEN):
        with self.lock:
            self.setcolor(self.logger.info,message,color)

    def war(self,message,color=FOREGROUND_YELLOW):
        with self.lock:
            self.setcolor(self.logger.warning,message,color)

    def error(self,message,color=FOREGROUND_RED):
        with self.lock:
            self.setcolor(self.logger.error,message,color)

    def cri(self,message,color=FOREGROUND_RED):
        with self.lock:
            self.setcolor(self.logger.critical, message, color)

if __name__ =='__main__':
    logyyx = Logger(path='yyx.log', c_level=logging.WARNING, f_level=logging.DEBUG)
    logyyx.debug('一个debug信息')
    logyyx.info('一个info信息')
    logyyx.war('一个warning信息')
    logyyx.error('一个error信息')
    logyyx.cri('一个致命critical信息')