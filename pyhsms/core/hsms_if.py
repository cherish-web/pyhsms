# _*_ coding: utf-8 _*_
#@Time      : 2020/8/14 上午 08:26
#@Author    : cherish_peng
#@Email     : 1058386071@qq.com
#@File      : hsms_if.py
#@Software  : PyCharm
from .item import Item
from .secsmessage import SecsMessage
from .errsecsmsg import ErrSecsMsg
import re
from .systembytegenerator import SystemByteGenerator
from .analysissml import sml
import threading
import time
from pathlib import Path

class Hsms_If:
    def __init__(self,path,callback):
        file = Path(path)
        if not file.is_file():
            raise Exception("the file({0}) isn't exsist".format(path))
        self.callback = callback
        self.sml =sml(path)
        self.msgdic, self.namesfdic,self.sfwdic,self.iflist,self.trigger= self.sml.read_analysis_sml()
        ErrSecsMsg.init_ErrSecsMsg(normsglist=list(self.sfwdic.keys()))
    def everytriggerevent(self):
        for name in self.trigger.keys():
            if name not in self.msgdic:
                raise Exception("triggerevent error : name {0} isn't exsist".format(name))
            sf = self.namesfdic[name]
            result = re.match(r'^S(\d{1,3})F(\d{1,3})$',sf)
            if not result:
                raise Exception('the value of Stream and Function get fail')
            s = int(result.groups()[0])
            f = int(result.groups()[1])
            everytime = int(self.trigger[name])
            item = Item.dictoitem({name:self.msgdic[name]})
            replyexpected = self.sfwdic[self.namesfdic[name]]
            msg = SecsMessage(item=item,name=name,s=s,f=f,replyexpected=replyexpected)
            thread = threading.Thread(target=self.senddatamessage,args=(msg,everytime))
            thread.setDaemon(True)
            thread.start()

    def iftriggerevent(self,msg:SecsMessage):
        for condition in self.iflist:
            if self.istriggerevent(msg=msg,condition=condition):
                if condition[1] in self.msgdic.keys():
                    result = re.match(r'^S(\d{1,2})F(\d{1,2})$', self.namesfdic[condition[1]])
                    if not result:
                        return
                    s = int(result.groups()[0])
                    f = int(result.groups()[1])

                    item = Item.dictoitem({condition[1]:self.msgdic[condition[1]]})
                    replyexpected = self.sfwdic[self.namesfdic[condition[1]]]
                    if replyexpected:
                        self.callback(SecsMessage(item=item, name=condition[1], s=s, f=f, replyexpected=replyexpected))
                    else:
                        self.callback(SecsMessage(item=item, name=condition[1], s=s, f=f, replyexpected=replyexpected,systembyte=msg.systembyte))

    def istriggerevent(self,msg:SecsMessage,condition):
        conditionstr = condition[0]
        result = re.match(r'(.*?) *\( *(\d{0,2}) *\) *(<|>|==|<=|>=) *<(.*?) +(.*?)>', conditionstr)
        if result:
            tup = result.groups()
            sf = tup[0].upper()
            if sf not in self.sfwdic:
                return False
                #raise Exception('the condition({0}) of iftriggerevent err'.format(conditionstr))

            if sf != 'S{0}F{1}'.format(msg.s,msg.f):
                return False
            index = int(tup[1])
            cal = tup[2]
            value = None
            if 'F' in tup[3]:
                value = round(float(tup[4]),5)
            elif re.match(r'I\d.*?|U\d.*?', tup[3]):
                value = int(tup[4])
            elif re.match(r'A.*?|Boolean.*?|B.*?', tup[3]):
                value = tup[4].strip('"').strip("'")

            if cal == '==':
                if value == msg.get_itemvaluebyindex(index):
                    return True
            elif cal == '<':
                if value < msg.get_itemvaluebyindex(index):
                    return True
            elif cal == '>':
                if value > msg.get_itemvaluebyindex(index):
                    return True
            elif cal == '<=':
                if value <= msg.get_itemvaluebyindex(index):
                    return True
            elif cal == '>=':
                if value >= msg.get_itemvaluebyindex(index):
                    return True
        else:
            conditionstr = conditionstr.upper()
            if conditionstr not in self.sfwdic:
                return False
                #raise Exception('the condition({0}) of iftriggerevent err'.format(conditionstr))
            if conditionstr == 'S{0}F{1}'.format(msg.s,msg.f):
                return True
        return False
    def senddatamessage(self,msg:SecsMessage,everytime):
        while True:
            try:
                msg = SecsMessage(item=msg.secsitem, name=msg.name, s=msg.s, f=msg.f, replyexpected=msg.replyexpected)
                self.callback(msg)
            except Exception as e:
                raise e
            time.sleep(everytime)
