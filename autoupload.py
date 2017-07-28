#!/usr/bin/python3
#coding=utf-8
import paramiko
import os
import datetime  
import threading
import logging

local_dir=os.getcwd()
remote_dir='/opt/local/bin/VOS/cur/' 
username='root'  
password='vos'  
port=22  

fmt = logging.Formatter('[%(levelname)s][%(asctime)s][%(name)s][%(lineno)d]--%(message)s')
LOG_FILE = 'autoupload.log'  



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
    
    t=paramiko.Transport((hostname,port)) 
    try: 
    	t.connect(username=username,password=password)  
    except Exception as e:
        log.error(e)
        fh.close()
    sftp=paramiko.SFTPClient.from_transport(t)
    log.info('backup start')
    
    log.info('upload file start  ' )  
    for root,dirs,files in os.walk(local_dir):  
        log.debug('[%s][%s][%s]' % (root,dirs,files))  
        for filespath in files:  
            local_file = os.path.join(root,filespath)  
            log.debug('[%s][%s][%s][%s]' % (root,filespath,local_file,local_dir))  
            a = local_file.replace(local_dir,'').replace('\\','/').lstrip('/')  
            log.debug('%s',  remote_dir)  
            remote_file = os.path.join(remote_dir,a)  
            log.debug('%s',remote_file)  
            try:  
                sftp.put(local_file,remote_file)  
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
     print("|       TSC      AutoUpload               |")
     print("|please enter real ip OR I'll crash for ya|")
     print('-------------------------------------------')
     r=input("tsc 数量:\n")
     hostname=[]
     for i in range (0,int(r)):
         hostname.append(input("tsc  ip:\n"))
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
     print ('complete %s' %datetime.datetime.now())

    
