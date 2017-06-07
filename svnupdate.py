#!usr/bin/python3 

import time,os,sys,svnconfig
import subprocess
from subprocess import call

dist=svnconfig.setting['dist']
os.chdir(svnconfig.setting['dist'])

def update():
    #svnconfig.setting['dist']=dist#+time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime())
    cmd='svn up --username %(user)s --password %(pwd)s'%svnconfig.setting
    print ("execute %s"%cmd)
    #print os.popen(cmd).read()
    return os.system(cmd)
    #return subprocess.Popen(cmd,shell=True)

while True:
    count = 0;
    ret=update()
    if(ret==0):
        print ('update success')
        break;
    else:
        print ('update fail')
    time.sleep(svnconfig.setting['interval'])
