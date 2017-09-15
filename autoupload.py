#!/usr/bin/python3
#coding=utf-8

import paramiko
import os,sys
#import datetime  
import threading
import logging
import re 
import time #sleep
now = time.strftime("%Y-%m-%d-%H-%M-%S")

local_dir=os.getcwd()
remote_dir='/opt/local/bin/VOS/cur/' 
username='root'  
password='vos'  
ppc_password=''
port=22  

fmt = logging.Formatter('[%(levelname)s][%(asctime)s][%(name)s][%(lineno)d]--%(message)s')
LOG_FILE = 'autoupload.log'  




class ShellHandler:

    def __init__(self, host, user, psw):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(host, username=user, password=psw, port=22)

        self.channel = self.ssh.invoke_shell()
        #self.stdin = channel.makefile('wb')
        #self.stdout = channel.makefile('r')

    def __del__(self):
        self.ssh.close()

    def execute(self, cmd):
        cmd += '\r'
        tp = re.compile(r'@VOS:~# ')
        mp = re.compile(r'root@') 
        while True:
            self.channel.send('sudo su\r')
            self.channel.send(cmd)
            time.sleep(0.5)
            result=''
            ret=self.channel.recv(65535)
            #ret=ret.decode('utf-8')
            result+=str(ret)
            #print(result)
            if tp.search(result) or mp.search(result) :
                print ("execute finished")
                break



def upload(local_dir,remote_dir,hostname):
    
    log=logging.getLogger(hostname)
    log.setLevel(logging.DEBUG)
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    log.addHandler(ch)
    
    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    log.addHandler(fh)

    log.info('backup start')
    sh=ShellHandler(hostname,username,password)
    
    
    cmd = 'mv ' + remote_dir  +' /opt/local/bin/VOS/cur-'+str(now)+'/'
    print (cmd)
    sh.execute(cmd)
    

    
    t=paramiko.Transport((hostname,port)) 
    try: 
    	t.connect(username=username,password=password)  
    except Exception as e:
        log.error(e)
        fh.close()
    sftp=paramiko.SFTPClient.from_transport(t)

    log.info('upload file start  ' )  
    for root,dirs,files in os.walk(local_dir):  
        #log.debug('[%s][%s][%s]' % (root,dirs,files))  
        for filespath in files:  
            local_file = os.path.join(root,filespath)  
            #log.debug('[%s][%s][%s][%s]' % (root,filespath,local_file,local_dir))  
            a = local_file.replace(local_dir,'').replace('\\','/').lstrip('/')  
            log.debug('%s',  remote_dir)  
            remote_file = os.path.join(remote_dir,a)  
            log.debug('%s',remote_file)  
            try:  
                sftp.put(local_file,remote_file)
                log.info('%s uploading',local_file)
            except Exception as e:  
                sftp.mkdir(os.path.split(remote_file)[0])  
                sftp.put(local_file,remote_file)  
                log.debug("upload %s to remote %s" % (local_file,remote_file))
                fh.close()
        for name in dirs:  
            local_path = os.path.join(root,name)  
            log.info("%s,%s",local_path,local_dir)  
            a = local_path.replace(local_dir,'').replace('\\','')  
            remote_path = os.path.join(remote_dir,a)  
            try:  
                sftp.mkdir(remote_path)  
                log.debug("mkdir path %s" % remote_path)  
            except Exception as e:
                log.error("mkdir path %s" % remote_path)
                #log.error(e)
    log.info('upload file success  ' )  
    t.close()  
    ch.close()
    fh.close()
    

          
if __name__=='__main__':
     print('-------------------------------------------')
     print("|           TSC  AutoUpload               |")
     print('|                                         |')
     print('-------------------------------------------')
     print(u'请将该程序放在上传文件的同级目录下')
     print(u'程序会将同目录下所有文件上传，所以整准点')
     print(u'如果崩溃把日志rtx给w18858或者skype wangqw2ee@outlook.com')

     hostname=[]
     for i in range (0,1):
         hostname.append(input(u"tsc ip (没有ip校验，别输错了):\n"))

     key=input(u"tsc 密码 默认回车:\n")
     if key != '':
         password=key
     threads = []
     for i in hostname:
         try :
             t = threading.Thread(target=upload,args=(local_dir,remote_dir,i))    
         except WinError as e:
            log.error(e)
            fh.close()
            
         threads.append(t)
         
     for t in threads:
         t.setDaemon(True)
         t.start()
    
     t.join()
     print ('complete %s' %now)

    
