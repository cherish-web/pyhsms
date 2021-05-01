# _*_ coding: utf-8 _*_
#@Time      : 2020/7/29 下午 02:25
#@Author    : cherish_peng
#@Email     : 1058386071@qq.com
#@File      : analysissml.py
#@Software  : PyCharm
import os
import re
import json
import ctypes


class sml:
    '''
    sml文件解析类
    '''
    def __init__(self,path):
        self.dicdata = {}
        self.smlpath = path
        self.sendbytimedic= {}
        self.namesfdic = {}
        self.sfwdic = {}
        self.iflist = []
    def readsml(self):
        '''
        读取sml文件内容
        :return: null
        '''
        flag = False
        self.dicdata = {}
        self.data = []
        with open(self.smlpath,'r') as f:
            for line in f:
                line=line.strip()
                if re.match(r'^/\*',line):
                    flag = True
                if re.match(r'(.*?)\*/$', line):
                    flag = False
                    continue
                if re.match(r'^(\s)?$', line):
                    continue
                if flag:
                    continue
                #print(line.strip())
                self.data.append(line)

    def analysistrigger(self,tepstr):
        result = re.match(r'^if \((.*?)\) (.*?)\.$', tepstr)
        if result:
            self.iflist.append((result.groups()[0].strip(), result.groups()[1].upper()))
            return True
        result = re.match(r'^every (\d{1,3}) send (.*?)\.$', tepstr)
        if result:
            self.sendbytimedic[result.groups()[1].strip().upper()] = int(result.groups()[0])
            return True
        return False

    def analysis(self,subdlist=[], flag=True, count=0):
        '''
        解析SECS sml文件内容
        :param subdlist: 临时存储同等级标签元素
        :param flag: 解析标签内容
        :param count: 解析起始行
        :return: list: 返回列表集合
        '''
        datadiclist=[]
        if count>len(self.data)-1:
            return subdlist, True, count
        if flag:
            tepstr = self.data[count].strip()
            if self.analysistrigger(tepstr):
                return self.analysis(count=count + 1)
            result = re.match(r'^(.*?):(.*?)(W?)$', tepstr)
            if result:
                name = result.groups()[0].strip().upper()
                sf = result.groups()[1].strip().strip("'").upper()
                replyflag = bool(result.groups()[2])
                self.sfwdic[sf] = replyflag
                self.namesfdic[name] = sf
                self.dicdata[name],_,count= self.analysis(flag=False,count=count+1)
                return self.analysis(count=count + 1)
            else:
                result = re.match(r'^([a-zA-z].*?)$', tepstr)
                if result:
                    result1=re.match(r'^(.*?)(W?)\.$', tepstr)
                    if result1:
                        name = result1.groups()[0].strip().upper()
                        replyflag = bool(result1.groups()[1])
                        self.sfwdic[name] = replyflag
                        self.namesfdic[name] = name
                        self.dicdata[name] = []
                    else:
                        result1 = re.match(r'^(.*?) (W)$', tepstr)
                        if result1:
                            name = result1.groups()[0].strip().upper()
                            replyflag = bool(result1.groups()[1])
                            self.sfwdic[name] = replyflag
                            self.namesfdic[name] = name
                            self.dicdata[name], _, count = self.analysis(flag=False, count=count + 1)
                        else:
                            if not re.match(r'\s', tepstr):
                                name = tepstr.strip().upper()
                                self.sfwdic[name] = False
                                self.namesfdic[name] = name
                                self.dicdata[name], _, count = self.analysis(flag=False, count=count + 1)
                self.analysis(count=count + 1)
        else:
            tepstr = self.data[count].strip()
            result = re.match(r'^(<|>)([A,J,B,L]|I1|I2|I4|U1|U2|U4|F4|F8|Boolean)?', tepstr)
            if not result:
                print("row:",count,tepstr)
                raise Exception("synax err")
            result = re.match(r'<L>\.?', tepstr)
            if result:
                datadiclist.append([])
                return self.analysis(subdlist=subdlist+datadiclist,flag=False, count=count + 1)
            result = re.match(r'^<L', tepstr)
            if result:
                data,flag,count =self.analysis(flag=False, count=count + 1)
                if flag:
                    #datadiclist.append(list(data))
                    return data,True,count
                else:
                    datadiclist.append(list(data))
                    data1, flag1, count = self.analysis(flag=False, count=count + 1)
                    datadiclist+=data1
                    return subdlist+datadiclist,flag1,count
            result = re.match(r'^< ?(.*?) +(.*?) ?>.?$', tepstr)
            if result:
                if self.data.__len__() > count:
                    datadic={}
                    datadic[result.groups()[0].split('[')[0]] = result.groups()[1].strip('"').strip("'")
                    datadiclist.append(datadic)
                    result = re.match(r'(.*?)>\.$', tepstr)
                    if result:
                        return subdlist+datadiclist,True,count
                    return self.analysis(flag=False, subdlist=subdlist+datadiclist, count=count + 1)
            result = re.match(r'^<(B)$', tepstr)
            if result:
                value = ''
                for index in range(count+1,self.data.__len__()):
                    tepstr = self.data[index].strip()
                    result1 = re.match(r'>.?$', tepstr)
                    if result1:
                        value = value.strip()
                        break;
                    if value:
                        value +=' '
                    value+= tepstr
                count = index
                datadic = {}
                datadic[result.groups()[0].split('[')[0]] = value
                datadiclist.append(datadic)
                tepstr1 = self.data[count].strip()
                result1 =re.match(r'>.$', tepstr1)
                if result1:
                    return subdlist+datadiclist,True,count
                return self.analysis(flag=False, subdlist=subdlist+datadiclist, count=count + 1)
            #tepstr = self.data[count].strip()
            result = re.match(r'^<(.*?)>$', tepstr)
            if result:
                datadic = {}
                datadic[result.groups()[0].split('[]')[0]]= ''
                datadiclist.append(datadic)
                return self.analysis(flag=False, subdlist=subdlist+datadiclist, count=count + 1)
            result = re.match(r'^>$', tepstr)
            if result:
                return subdlist, False, count
            #tepstr = self.data[count].strip()
            result = re.match(r'^> ?\.$', tepstr)
            if result:
                return subdlist, True, count
    def read_analysis_sml(self):
        '''
        读取并解析sml文档
        :return: （dicdata,namesfdic,sfwdic,iflist,sendbytimedic）
        :dicdata: {消息name： msgbody}
        self.namesfdic ： {消息name： SxFy}
        self.sfwdic ： {SxFy： replyflag}
        self.iflist ： {表达式： 消息name}
        self.sendbytimedic {消息name： time}
        '''
        self.dicdata.clear()
        self.sfwdic.clear()
        self.namesfdic.clear()
        self.iflist.clear()
        self.readsml()
        self.analysis()
        return self.dicdata,self.namesfdic,self.sfwdic,self.iflist,self.sendbytimedic
if __name__ == '__main__':
    mysml = sml('sampl.sml')
    dic,namesfdic,sfwdic,iflist,_ = mysml.read_analysis_sml()
    print(iflist)
    print(namesfdic)
    print(sfwdic)
    print(dic)
