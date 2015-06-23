#!/usr/bin/env python
# _*_ coding: utf-8 _*_

"""
这是日志记录模块，包含所有的记录日志的方法
"""

import threading
lock=threading.Lock()

def _log_accept(owner,file):
    try:
        fh=open(file,'a+')
        fh.write("%s - - [%s] %s\n" %
                         (owner.client_address[0],
                          owner.log_date_time_string(),
                          owner.requestline))
    except:
        print "can not open file:%s\n"%file
    finally:
        fh.close()

def _log_blacklist(owner,file):
    try:
        fh=open(file,"a+")
        fh.write("%s    ## - -date: [%s]"%(owner.client_address[0],owner.log_date_time_string))
    except:
        print "can not open file:%s\n"%file
    finally:
        fh.close()

def _log_deny(owner,file,*args):
    try:

        lock.acquire()
        fh=open(file,'a+')
        fh.write("%s - - [%s] %s\nquery - - %s\npattern - - %s\n\n" %
                         (owner.client_address[0],
                          owner.log_date_time_string(),
                          owner.requestline,args[0],args[1]))
    except :
        print "can not open file:%s\n"%file
    finally:
        fh.close()
        lock.release()

def log_message(owner,file,*args):
    if file=='connectAccept.db':
        _log_accept(owner,file)
    if file=='blacklist.db':
        _log_blacklist(owner,file)
    if file=='connectDeny.db':
        _log_deny(owner,file,*args)



