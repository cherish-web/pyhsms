# _*_ coding: utf-8 _*_
#@Time      : 2020/7/29 上午 10:45
#@Author    : cherish_peng
#@Email     : 1058386071@qq.com
#@File      : secsgem.py
#@Software  : PyCharm
from .streamdecoder import Streamdecoder
from .messagetype import MessageType
from .secsmessage import SecsMessage
from .errsecsmsg import ErrSecsMsg,ErrSecsMsgType
from .connectionstate import ConnectionState
from .logger.logger import Logger
import threading
from threading import Timer
import socket
import select
import time

class SecsGem:
    def __init__(self,isactive:bool,ip:str,port:int,receivebuffersize=1024,deviceid=0xffff,timeoutdic={}):
        self.deviceid=deviceid
        ErrSecsMsg.init_ErrSecsMsg(self.deviceid)
        self.loger = Logger.getlogger()
        self.T3 = timeoutdic.get('T3',45)
        self.T5 = timeoutdic.get('T5',10)
        self.T6 = timeoutdic.get('T6',5)
        self.T7 = timeoutdic.get('T7',10)
        self.T8 = timeoutdic.get('T8',5)
        self.sock = None
        self.eqp = None
        self.linktestinterval = 30
        self.linktestenable = True
        self.isactive = isactive
        self.ipaddress = ip
        self.port=port
        self.lock = threading.Lock()
        self.lock1 = threading.Lock()
        self.lock2 = threading.Lock()
        self.decoderbuffersize=receivebuffersize
        self.timer_requestdic = {}
        self.timer5 = Timer(3, self.timer5func)
        self.timer7 = Timer(self.T7, self.timer7func)
        self.timer8 = Timer(self.T8, self.timer8func)
        self.timerLinkTest=threading.Thread(target=self.timer_linktestfunc,args=(self.linktestinterval,))
        self.timerLinkTest.setDaemon(True)
        self.state = ConnectionState.DisConnected
        self.MessageIn = self.messagein
        self.SendMessageFail = self.sendmesgfail
        self.ConnectedStateChange = self.connectedstatechange
        self.secsmainthreadlife = True
        self.subthreadlife = True

        self.secsmainthread = threading.Thread(target=self.mainthread)
        self.secsmainthread.setDaemon(True)

    def start(self):
        self.timerLinkTest.start()
        self.secsmainthread.start()

    def removetimer_requestdic(self,systembyte:int):
        with self.lock2:
            del self.timer_requestdic[systembyte]

    def mainthread(self):
        while self.secsmainthreadlife:
            self.timer5 = Timer(self.T5, self.timer5func)
            self.timer5.setDaemon(True)
            self.timer5.start()
            while self.subthreadlife:
                time.sleep(1)
            self.communicationstatechanging(ConnectionState.DisConnected)
            self.subthreadlife = True
            self.reset()
            if not self.secsmainthreadlife:
                if self.isactive:
                    if self.state == ConnectionState.Selected:
                        self.sendcontrolmessage(MessageType.SeperateRequest)
                        self.sock.close()
                else:
                    if self.state == ConnectionState.Selected:
                        self.sendcontrolmessage(MessageType.SeperateRequest)
                        self.sock.close()
                    if self.eqp:
                        self.eqp.close()

    def timer3func(self,msg:SecsMessage):
        if msg.systembyte in self.timer_requestdic:
            self.senddatamessage(ErrSecsMsg.get_errmsg(errmsgtype=ErrSecsMsgType.TransactionTimerTimeout,msg=msg))
            self.removetimer_requestdic(msg.systembyte)
        self.loger.war('T3 Timeout: {0} {1}'.format(msg,msg.systembyte))

    def timer5func(self):
        if self.isactive:
            self.connecteqp()
        else:
            self.eqplisten()

    def timer6func(self,msg:SecsMessage):
        if msg.systembyte in self.timer_requestdic:
            self.senddatamessage(ErrSecsMsg.get_errmsg(errmsgtype=ErrSecsMsgType.ConversationTimeout, msg=msg))
            self.removetimer_requestdic(msg.systembyte)
            if self.state in (ConnectionState.Selected,ConnectionState.Connected):
                try:
                    self.sock.close()
                except Exception as e:
                    pass
                self.loger.debug("T6 Timeout, Closed Remote Client!")
            if self.isactive:
                self.communicationstatechanging(ConnectionState.Retry)
            else:
                self.communicationstatechanging(ConnectionState.DisConnected)
        self.loger.war('T6 Timeout: {0}'.format(msg))
    def timer7func(self):
        if self.isactive:
            self.communicationstatechanging(ConnectionState.Retry)
        else:
            self.sendcontrolmessage(MessageType.SeperateRequest)
            try:
                self.sock.close()
            except Exception as e:
                pass
            self.loger.debug("Select Timeout,Closed Remote Client!")
            Streamdecoder.BUFFER.clear()
        self.loger.war('T7 Timeout')

    def timer8func(self):
        self.sendcontrolmessage(MessageType.SeperateRequest)
        if self.state == ConnectionState.Selected:
            try:
                self.sock.close()
            except:
                self.loger.debug('Data Transfer Timeout, Closed Remote Client!')
            if self.isactive:
                self.communicationstatechanging(ConnectionState.Retry)
            else:
                Streamdecoder.BUFFER.clear()
        self.loger.info('T8 Timeout')

    def timer_linktestfunc(self,linktestinterval):
        while self.secsmainthreadlife:
            if self.state==ConnectionState.Selected:
                self.loger.info('Send Linktest.req.')
                self.sendcontrolmessage(MessageType.LinkTestRequest)
            time.sleep(linktestinterval)
    def sendcontrolmessage(self,msgtype:MessageType,systembyte=None):
        msg = SecsMessage(deviceid=self.deviceid, msgtype=msgtype, systembyte=systembyte)
        bts = msg.encode()
        if msgtype in (MessageType.LinkTestRequest, MessageType.SelectRequest):
            time6 = Timer(interval=self.T6,function=self.timer6func,args=(msg,))
            time6.setDaemon(True)
            self.timer_requestdic[msg.systembyte] = time6
            time6.start()
        self.sendmessage(bts)
        self.loger.debug('Send: {0} {1} {2}'.format(msg,msg.msgtype,msg.systembyte))

    def senddatamessage(self,msg:SecsMessage):
        if self.state != ConnectionState.Selected:
            self.SendMessageFail(msg=msg)
            return
        msg.deviceid=self.deviceid
        bts = msg.encode()
        if msg.replyexpected:
            time3 = Timer(interval=self.T3,function=self.timer3func,args=(msg,))
            time3.setDaemon(True)
            self.timer_requestdic[msg.systembyte] = time3
            time3.start()
        self.sendmessage(bts)
        self.loger.info('Send: {0} {1}'.format(msg,msg.systembyte))

    def sendmessage(self,bts:bytearray):
        try:
            if isinstance(self.sock,socket.socket):
                self.sock.sendall(bts)
        except Exception as e:
            self.communicationstatechanging(ConnectionState.Retry)

    def reset(self):
        time.sleep(1)
        if self.timer7.is_alive():
            self.timer7.cancel()
        with self.lock1:
            for timern in self.timer_requestdic.values():
                if timern:
                    if timern.is_alive():
                        timern.cancel()
            self.timer_requestdic.clear()

        if self.timer8.is_alive():
            self.timer8.cancel()
        Streamdecoder.BUFFER.clear()

    def connectedstatechange(self,State:ConnectionState):
        pass

    def communicationstatechanging(self,newState:ConnectionState):
        self.ConnectedStateChange(newState)
        with self.lock:
            self.state = newState
            if self.state == ConnectionState.Selected:
                if self.timer7.is_alive():
                    self.timer7.cancel()
                    self.loger.info('T7 stop ')
            elif self.state == ConnectionState.Connected:
                if self.timer7.is_alive():
                    self.timer7.cancel()
                self.loger.info('T7 start ')
                self.timer7 = Timer(self.T7,self.timer7func)
                self.timer7.setDaemon(True)
                self.timer7.start()
            elif self.state == ConnectionState.Retry and self.isactive:
                self.subthreadlife = False
            elif self.state == ConnectionState.Connecting:
                if self.timer7.is_alive():
                    self.timer7.cancel()
                    self.loger.info('T7 stop ')

    def connecteqp(self):
        self.communicationstatechanging(ConnectionState.Connecting)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.ipaddress, self.port))
            self.loger.info("HSMS Communication Start!")
            self.communicationstatechanging(ConnectionState.Connected)
            recthread = threading.Thread(target=self.msgrecive)
            recthread.setDaemon(True)
            recthread.start()
            self.sendcontrolmessage(MessageType.SelectRequest)
        except Exception as e:
            self.loger.war("HSMS Communication Fail!")
            self.communicationstatechanging(ConnectionState.Retry)

    def msgrecive(self):
        outputs =[]
        intputs = [self.sock]
        while self.subthreadlife:
            try:
                readable, writable, exceptional = select.select(intputs, outputs, intputs)
                for sock in readable:
                    try:
                        data = sock.recv(self.decoderbuffersize)
                        if not data:
                            raise Exception('Remote Disconnect')
                        if self.messagedatatosecsmsg(data):
                            raise Exception('Remote active Disconnection')
                    except ConnectionError as ce:
                        sock.close()
                        raise ce
            except Exception as err:
                if self.isactive:
                    self.loger.info("HSMS Communication Disconnected!")
                else:
                    self.loger.info('Remote Client Disconnected!')
                self.loger.debug("Msgrecive Exception: {0}".format(err))
                break
        if self.isactive:
            self.communicationstatechanging(ConnectionState.Retry)
        else:
            self.communicationstatechanging(ConnectionState.DisConnected)
            Streamdecoder.BUFFER.clear()

    def eqplisten(self):
        self.eqp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.eqp.bind((self.ipaddress, self.port))
        except Exception as e:
            self.subthreadlife = False
            self.eqp = None
            self.loger.war("HSMS Socket Bind Error: {0}".format(e))
            return
        self.loger.info("HSMS Communication Started!")
        self.eqp.listen(1)

        while self.subthreadlife:
            client, addr = self.eqp.accept()
            if self.state in (ConnectionState.Selected,ConnectionState.Connected):
                try:
                    self.loger.debug("New Remote Client Connected , Closing Connected Socket!")
                    self.sock.close()
                except Exception as e:
                    self.loger.debug("Closed Connected Socket: {0}".format(e))
            self.loger.info("Remote Client Connected!")
            self.sock = client
            eqp_thread = threading.Thread(target=self.msgrecive)
            eqp_thread.setDaemon(True)
            eqp_thread.start()
            self.communicationstatechanging(ConnectionState.Connected)
    def messagedatatosecsmsg(self, data):
        if self.timer8.is_alive():
            self.timer8.cancel()
        li = Streamdecoder.decode(data)
        if Streamdecoder.BUFFER:
            self.timer8 = Timer(self.T8,self.timer8func)
            self.timer8.setDaemon(True)
            self.timer8.start()
        for msg in li:
            if msg.systembyte in self.timer_requestdic:
                if self.timer_requestdic[msg.systembyte].is_alive():
                    self.timer_requestdic[msg.systembyte].cancel()
                    self.removetimer_requestdic(msg.systembyte)
            if msg.msgtype == MessageType.LinkTestRequest:
                self.loger.info('Receive Linktest.req.')
                self.sendcontrolmessage(MessageType.LinkTestResponse, msg.systembyte)
                self.loger.info('Send Linktest.rsp.')
            elif msg.msgtype == MessageType.LinkTestResponse:
                self.loger.info('Receive Linktest.rsp.')
            elif msg.msgtype == MessageType.SelectRequest:
                self.communicationstatechanging(ConnectionState.Selected)
                self.sendcontrolmessage(MessageType.SelectResponse, msg.systembyte)
            elif msg.msgtype == MessageType.SelectResponse:
                self.communicationstatechanging(ConnectionState.Selected)
            elif msg.msgtype == MessageType.SeperateRequest:
                if self.isactive:
                    self.communicationstatechanging(ConnectionState.DisConnected)
                else:
                    return True
            #print(msg.tosml())
            elif msg.msgtype == MessageType.DataMessage:
                errmsgtype = ErrSecsMsg.iserrmsg(msg)
                if errmsgtype:
                    if errmsgtype != ErrSecsMsgType.ErrSecsMsgReply:
                        self.senddatamessage(ErrSecsMsg.get_errmsg(errmsgtype=errmsgtype,msg=msg))
                        continue
                    else:
                        pass
                self.loger.info('Receive: {0} {1}'.format(msg, msg.systembyte))
                msginthread = threading.Thread(target=self.MessageIn,args=(msg,))
                msginthread.setDaemon(True)
                msginthread.start()
        return False
    def messagein(self,msg:SecsMessage):
        pass
    def sendmesgfail(self,msg:SecsMessage):
        pass
