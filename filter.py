#!/usr/bin/env python
# _*_ coding: utf-8  _*_

"""
过滤模块，对内容进行分析，根据过滤规则
进行合法性检测
"""

import urllib,re
from log import log_message

class SQLFilter(object):
    patterns=None

    #将url编码转化为标准编码，并且统一为小写字母
    #data格式为(scm,netloc,path,params,query,fragment)
    def _ParseData(self,data):
        return urllib.unquote(data).lower()

    def detect(self,owner,data):
        (scm,netloc,path,params,query,fragment)=data
        text=self._ParseData(query)
        ret=re.search(':',text)
        if ret:
            if re.search('http://',text)==None:
                return False

        for item in self.patterns:
            ret=item.search(text)
            if ret!=None:
                log_message(owner,'connectDeny.db',*(text,item.pattern))
                print "can not pass pattern:\t%s\n"% item.pattern
                return False
        return True



