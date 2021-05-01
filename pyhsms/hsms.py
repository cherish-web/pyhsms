# _*_ coding: utf-8 _*_
#@Time      : 2020/8/18 下午 01:39
#@Author    : cherish_peng
#@Email     : 1058386071@qq.com
#@File      : hsms.py
#@Software  : PyCharm
from .core.secsgem import SecsGem
from .core.hsms_if import Hsms_If
from .core.secsmessage import SecsMessage
from .core.connectionstate import ConnectionState
import signal
import sys
import time
class Hsms:
    def __init__(self,isactive:bool,ip:str,port:int,receivebuffersize=1024,deviceid=0xffff,timeoutdic={},**kwagrs):
        self.life =True
        sys.setrecursionlimit(3000)
        self.sc = SecsGem(isactive=isactive, ip=ip, port=port, receivebuffersize=receivebuffersize,
                          deviceid=deviceid,timeoutdic=timeoutdic)
        self.callback1 = None
        if 'callback1' in kwagrs.keys():
            self.callback1 = kwagrs.get('callback1')
        self.sc.MessageIn = self.messagein
        self.callback2 = None
        if 'callback2' in kwagrs.keys():
            self.callback2 = kwagrs.get('callback2')
        self.sc.SendMessageFail = self.sendmessagefail
        self.callback3 = None
        if 'callback3' in kwagrs.keys():
            self.callback3 = kwagrs.get('callback3')
        self.sc.ConnectedStateChange = self.connectedstatechange
        self.smlpath = 'sample.sml'
        if 'smlpath' in kwagrs.keys():
            self.smlpath = kwagrs.get('smlpath')
        self.hsms_if_init()
        print('Read {0} SECS-II Messages from {1}'.format(len(self.hsms_if.msgdic.keys()),self.smlpath))
        print('Read {0} Trig Settings from {1}'.format(len(self.hsms_if.iflist)+len(self.hsms_if.trigger),self.smlpath))
        print('Quit the HSMS with CTRL-BREAK.')

    def hsms_if_init(self):
        self.hsms_if = Hsms_If(path=self.smlpath, callback=self.sendmessage)

    def run(self):
        signal.signal(signal.SIGINT, self.sigint_handler)
        signal.signal(signal.SIGTERM, self.sigint_handler)
        self.sc.start()
        self.hsms_if.everytriggerevent()

    def sigint_handler(self,signum, e):
        self.sc.secsmainthreadlife = False
        self.sc.subthreadlife = False
        time.sleep(1)
        self.life = False

    def forever(self):
        while self.life:
            time.sleep(1)

    def messagein(self,msg:SecsMessage):
        self.hsms_if.iftriggerevent(msg)
        if self.callback1:
            self.callback1(msg)

    def sendmessage(self,msg:SecsMessage):
        if self.sc.state == ConnectionState.Selected:
            self.sc.senddatamessage(msg=msg)

    def sendmessagefail(self,msg:SecsMessage):
        if self.callback2:
            self.callback2(msg)
    def connectedstatechange(self,state:ConnectionState):
        if self.callback3:
            self.callback3(state)