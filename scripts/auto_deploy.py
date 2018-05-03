#!/usr/bin/python3
#coding=utf-8

import paramiko
import os,sys
import logging
import re
import time

now = time.strftime("%Y-%m-%d-%H-%M-%S")
##------------ logging-----------------------

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


##---------------------dirs-------------------
##DO NOT USE DERICTLY!
local_dir=os.getcwd()
local_remotepath_dir=local_dir + '\\remotepath'
local_mycnf_dir=local_dir +'\\mycnf'
remote_dir='/opt/local/bin/VOS/cur/'
#remote_dir='/opt/cur/'
remote_db_dir='/opt/local/bin/VOS/db/db_install/'
remote_path_dir='/opt/remotepath/'
#remote_mycnf_dir='/etc/'
username='root'  
password='vos'  
ppc_password=''
port=22


def remove_back_slash(string):
    if string[-1] is '/':
        return string[:-1]

class FolderContainsBase(object):
    folder_contains_list=['unknown','tsc','db','mso']
    method_list=['do_nothing','backup','upload','invoke']
    folder_contains='unknown'
    local_dir = os.getcwd()

    def __init__(self,name):
        self.set_folder_type(name)
        log.info(name )
    
    def do_nothing(self):
        log.debug('base do nothing')

    def backup(self):
        log.debug('base backup')

    def upload(self):
        log.debug('base upload')
        
    def invoke(self):
        log.debug('base invoke')

    def set_folder_type(self, name):
        self.folder_contains = name


class TscFiles(FolderContainsBase):
    def backup(self):
        log.debug('TscFiles backup')

    def upload(self):
        log.debug('TscFiles upload')
        
    def invoke(self):
        log.debug('TscFiles invoke') 
        


class MsoFiles(FolderContainsBase):
    def backup(self):
        log.debug('MsoFiles backup')

    def upload(self):
        log.debug('MsoFiles upload')
        
    def invoke(self):
        log.debug('MsoFiles invoke')
        
class DbFiles(FolderContainsBase):
    def backup(self):
        log.debug('DbFiles backup')

    def upload(self):
        log.debug('DbFiles upload')
        
    def invoke(self):
        log.debug('DbFiles invoke')

class AutoDeploy(FolderContainsBase):
    instance=None
    def __init__(self):
        def check_folder_type():
            for _, _ ,filenames in os.walk(local_dir):                        
                if "source_mso" in filenames:
                    return 'db'
                elif "LLC.exe" in filenames:
                    return 'tsc'
                elif "CRT.exe" in filenames:
                    return 'mso'
        folder_type = check_folder_type()
        if folder_type is 'tsc':
            self.instance=TscFiles(folder_type)
        elif folder_type is 'mso':
            self.instance=MsoFiles(folder_type)
        elif folder_type is 'db':
            self.instance=DbFiles(folder_type)
        else:
            log.error(folder_type +'unimplement! quit!')
            time.sleep(60)
            quit(-1)

        self.backup()
        self.upload()
        self.invoke()

    def backup(self):
       self.instance.backup()

    def upload(self):
        self.instance.upload()
        
    def invoke(self):
        self.instance.invoke()


if __name__ == '__main__':
    print('-------------------------------------------')
    print("|           TSC  AutoDeploy               |")
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
    
    AutoDeploy()
    log.info ('complete %s' %now)
    
