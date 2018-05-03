#!/usr/bin/python3
#coding=utf-8
#TODO: tai luan le, dei chong xie
import paramiko
import os,sys
#import datetime  
import threading
import logging
import re 
import time #sleep
now = time.strftime("%Y-%m-%d-%H-%M-%S")

from enum import IntEnum

class FolderContains(IntEnum):
        tsc=0
        mso=1
        db=2

import shutil

local_dir=os.getcwd()
local_remotepath_dir=local_dir + '\\remotepath'
local_mycnf_dir=local_dir +'\\mycnf'
remote_dir='/opt/local/bin/VOS/cur/'
#remote_dir='/opt/cur/'
remote_db_dir='/opt/local/bin/VOS/db/db_install/'
remote_path_dir='/opt/remotepath/'
remote_mycnf_dir='/etc/'
username='root'  
password='vos'  
ppc_password=''
port=22  

fmt = logging.Formatter('[%(levelname)s][%(asctime)s][%(name)s][%(lineno)d]--%(message)s')
LOG_FILE = 'upload-'+now+'.log'  
log=logging.getLogger()
log.setLevel(logging.DEBUG)
                                
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(fmt)
log.addHandler(ch)
                    
fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging.DEBUG)
fh.setFormatter(fmt)
log.addHandler(fh)


def remove_back_slash(string):
    if string[-1] is '/':
        return string[:-1]

def check_what_contains(folder):
        for _, _ ,filenames in os.walk(folder):                        
                if "source_mso" in filenames:
                        return FolderContains.db
                elif "LLC.exe" in filenames:
                        return FolderContains.tsc
                elif "CRT.exe" in filenames:
                        return FolderContains.mso

folder_contains = check_what_contains(local_dir)


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
            if folder_contains is FolderContains.tsc:
                    self.channel.send('sudo su\r')
                    
            self.channel.send(cmd)
            time.sleep(0.5)
            result=''
            ret=self.channel.recv(65535)
            #ret=ret.decode('utf-8')
            result+=str(ret)
            #print(result)
            if tp.search(result) or mp.search(result) :
                log.debug ("execute finished")
                break





def prepare_db_folder(contains):
        if contains is FolderContains.db:
                file_list = ["hss_tsc","sqlite3","offline_bill","tsc"]
                mycnf="my.cnf"
                if os.path.exists(local_remotepath_dir) is False:
                        os.mkdir(local_remotepath_dir)
                        for f in file_list:
                                if os.path.isfile(local_dir+"\\" + f):
                                        shutil.copyfile(local_dir+"\\" + f,local_remotepath_dir+"\\"+f)
                                else:
                                        log.warn("missing "+f)
                if os.path.exists (local_mycnf_dir) is False:
                        os.mkdir(local_mycnf_dir)
                        shutil.copyfile(local_dir +"\\"+mycnf, local_mycnf_dir +"\\"+mycnf)
                        
                        
                
        

def upload(local_dir,remote_dir,hostname):

    log.info('backup start')
    sh=ShellHandler(hostname,username,password)
    
    cmd = 'mv ' + remote_dir  + ' ' +remove_back_slash(remote_dir)+ '-'+str(now)+'/'
    log.info (cmd)
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
    
    if folder_contains is not FolderContains.db:
                log.info('kill VOS instance to restart')
                cmd = 'kill `pgrep -n VOS.exe`'
                sh.execute(cmd)

    if folder_contains is FolderContains.db:
        cmd = 'chmod 777 ' + remove_back_slash(remote_dir ) +'/' +'*'
        sh.execute(cmd)
        
                
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
        hostname.append(input(u"ip (没有ip校验，别输错了):\n"))

    key=input(u"密码 默认vos:\n")
    if key != '':
        password=key

    for i in hostname:
        try :
                        if folder_contains is FolderContains.db:
                                prepare_db_folder(folder_contains)
                                upload(local_dir,remote_db_dir,i)                                
                                upload(local_remotepath_dir,remote_path_dir,i)
                                #upload(local_mycnf_dir,remote_mycnf_dir,i)
                        else:
                                upload(local_dir,remote_dir,i)
                                
        except WinError as e:
            log.error(e)
            fh.close()

     

        log.info ('complete %s' %now)

    
