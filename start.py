#!/usr/bin/env python
# _*_ coding: utf-8 _*_

__author__='fang'

import socket,re
from config import SimpleConfig
from httpProxy import ProxyHandler,serving,ThreadingHTTPServer
from filter import SQLFilter

if __name__=='__main__':

    try:
        #获取proxy的配置,返回一个dict
        #获取黑名单,返回一个list
        #获取过滤规则,返回一个list
        confile=SimpleConfig('proxy.cnf').config_proxy()
        refuseClients=SimpleConfig('blacklist.db').config_blacklist()
        filterPatterns=SimpleConfig('filterPattern.cnf').config_filter()

        #初始化SQLFilter的过滤规则
        patterns=[]
        for item in filterPatterns:
            pattern=re.compile(item)
            patterns.append(pattern)
        SQLFilter.patterns=patterns

        #初始化黑名单
        refuse=[]
        for c in refuseClients:
            client=socket.gethostbyname(c)
            refuse.append(client)
        ProxyHandler.blacklist=refuse
        ProxyHandler.buffer={}     #client=count 如果count达到5 则将client加入黑名单

        if confile.get('httphost'):
            server_address=(confile.get('httphost'),confile.get('httpport'))
        serving(ProxyHandler,ThreadingHTTPServer,server_address)
    finally:
        pass