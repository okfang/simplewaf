# _*_ coding:utf-8 _*_

__author__ = 'fang'

#配置信息文件，基本格式：key=value
class SimpleConfig:
    def __init__(self,file):
        self._file=file

    def config(self):
        if self._file=='proxy.cnf':
            return self.config_proxy(self._file)

        if self._file=='filterPattern.cnf':
            return self.config_filter(self._file)

        if self._file=='refuseClients.cnf':
            return self.config_blacklist(self._file)


    #处理proxy的配置信息，返回其中的key,value的dict
    def config_proxy(self):
        try:
            file=self._file
            props={}
            fh=open(file,'r')
            lines=fh.readlines()
            for text in lines:
                pos=text.find('##')
                if pos!=-1:
                    text=text[:pos]
                pairs=text.split('=')
                key=pairs[0].strip()
                value=pairs[1].strip()
                props[key]=value
            return props
        except:
            print "can not opnen ",file
            return

    #处理过滤规则,返回规则的列表
    def config_filter(self):
        try:
            file=self._file
            props=[]
            fh=open(file,'r')
            lines=fh.readlines()
            for text in lines:
                pos=text.find('##')
                if pos!=-1:
                    text=text[:pos]
                item=text.strip()
                props.append(item)
            return props
        except:
            print "can not open ",file
            return

    #处理黑名单
    def config_blacklist(self):
        try:
            file=self._file
            props=[]
            fh=open(file,'r')
            lines=fh.readlines()
            for text in lines:
                pos=text.find('##')
                if pos!=-1:
                    text=text[:pos]
                item=text.strip()
                props.append(item)
            return props
        except:
            print "can not opnen ",file
            return