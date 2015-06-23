#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import BaseHTTPServer,select,socket
import os,sys
import urlparse,SocketServer
import urllib,threading
from filter import SQLFilter
from log import log_message


__version__='0.1.1'


class ProxyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    __base=BaseHTTPServer.BaseHTTPRequestHandler
    __base_handle=__base.handle
    server_version = "litewaf/"+__version__

    lock=threading.Lock()

    def handle(self):
        print 'client incoming'
        (ip,port)=self.client_address
        if hasattr(ProxyHandler,'blacklist') and ip in ProxyHandler.blacklist: #判断是否在黑名单内
            self.raw_requestline=self.rfile.readline()
            if self.parse_request():
                self.send_error(403)
        else:
            self.__base_handle()

    def _connect_to(self,netloc,soc):
        print "start to connet to original Server"
        pos =netloc.find(':')
        if pos>0:
            host_port=netloc[:pos],int(netloc[pos+1:])
        else:
            host_port=netloc,80
        try:
            soc.connect(host_port)
        except socket.error,arg:
            try:
                msg=arg[1]
            except:
                msg=arg
            self.send_error(404,msg)
            return  0
        return 1



    def do_CONNECT(self):
        soc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            if self._connect_to(self.path,soc):
                self.log_request(200)
                self.wfile.write(self.protocol_version+"200 Connetciont establish\r\n")
                self.wfile.write("proxy-agent:%s\r\n"%self.version_string())
                self.wfile.write('\r\n')
                self._read_write(soc)
        finally:
            print '\r'"bye"
            soc.close()
            self.connection.close()

    def do_GET(self):
        soc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        (scm,netloc,path,params,query,fragment)=urlparse.urlparse(self.path,'http')

        ###########解码url编码##################
        query=urllib.unquote(query)
        print "query:%s\n"%query.lower()
        #############################

        pairs=(scm,netloc,path,params,query,fragment)
        print self.path
        if not netloc:
            netloc=self.headers.get('host',"")

        if scm!='http' or fragment or not netloc:
            self.send_error(400,"bad url %s"%self.path)
            return
        """
            sql注入检测
        """
        ret=SQLFilter().detect(self,pairs)
        if ret==False:
            ProxyHandler.lock.acquire()
            if ProxyHandler.buffer.get(self.client_address[0]):
                ProxyHandler.buffer[self.client_address[0]]+=1
            else:
                ProxyHandler.buffer[self.client_address[0]]=0
            if ProxyHandler.buffer[self.client_address[0]]>=5:
                ProxyHandler.buffer.pop(self.client_address[0])
                ProxyHandler.blacklist.append(self.client_address[0])

            ProxyHandler.lock.release()
            print "\t" "bye"
            soc.close()
            self.connection.close()
            return

        try:
            if self._connect_to(netloc,soc):
                log_message(self,'connectAccept.db')         #记录成功连接日志
                self.log_request()
                soc.send("%s %s %s\r\n"%(self.command,urlparse.urlunparse(('','',path,params,query,'')),
                                                 self.request_version))
                self.headers['Connection']='close'
                del self.headers['Proxy-Connection']
                for key_val in self.headers.items():
                    soc.send("%s: %s\r\n" %key_val)
                soc.send("\r\n")
                self._read_write(soc)
        finally:
            print "\t" "bye"
            soc.close()
            self.connection.close()

    def _read_write(self,soc,max_idling=20):
        iw=[self.connection,soc]
        ow=[]
        count=0
        datacnt=0
        isOkPageResponse=False
        while 1:
            count+=1
            datacnt+=1
            (ins,_,exs)=select.select(iw,ow,iw,3)
            if ins:
                for i in ins:
                    if i is soc:
                        out=self.connection
                    else:
                        out=soc

                    data=i.recv(8192)
                    if data:
                        out.send(data)
                        count=0
                    else:
                        if not isOkPageResponse:
                            return
            else:
                pass
            if count==max_idling:
                print "idling exit"
                break

    do_HEAD=do_GET
    do_POST=do_GET
    do_PUT=do_GET
    do_DELETE=do_GET

class ThreadingHTTPServer(BaseHTTPServer.HTTPServer,SocketServer.ThreadingMixIn):
    pass

def serving(HandlerClass,ServerClass,protocol="HTTP/1.0",server_address=('127.0.0.1',8000)):

    HandlerClass.protocol_version=protocol
    httpd=ServerClass(server_address,HandlerClass)
    sa=httpd.socket.getsockname()
    print "127.0.0.1@fang v1.0"
    print "serving HHTP on",sa[0],"port:",sa[1],""
    httpd.serve_forever()