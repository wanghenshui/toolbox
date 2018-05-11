#!/usr/bin/python3
#coding=utf-8

import paramiko
import os,sys
import logging
import re
import time
import shutil
now = time.strftime("%Y-%m-%d-%H-%M-%S")

##--------------log color--------------------
## can't work
def add_coloring_to_emit_windows(fn):
        # add methods we need to the class
    def _out_handle(self):
        import ctypes
        return ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
    out_handle = property(_out_handle)

    def _set_color(self, code):
        import ctypes
        # Constants from the Windows API
        self.STD_OUTPUT_HANDLE = -11
        hdl = ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
        ctypes.windll.kernel32.SetConsoleTextAttribute(hdl, code)

    setattr(logging.StreamHandler, '_set_color', _set_color)

    def new(*args):
        FOREGROUND_BLUE      = 0x0001 # text color contains blue.
        FOREGROUND_GREEN     = 0x0002 # text color contains green.
        FOREGROUND_RED       = 0x0004 # text color contains red.
        FOREGROUND_INTENSITY = 0x0008 # text color is intensified.
        FOREGROUND_WHITE     = FOREGROUND_BLUE|FOREGROUND_GREEN |FOREGROUND_RED
       # winbase.h
        STD_INPUT_HANDLE = -10
        STD_OUTPUT_HANDLE = -11
        STD_ERROR_HANDLE = -12

        # wincon.h
        FOREGROUND_BLACK     = 0x0000
        FOREGROUND_BLUE      = 0x0001
        FOREGROUND_GREEN     = 0x0002
        FOREGROUND_CYAN      = 0x0003
        FOREGROUND_RED       = 0x0004
        FOREGROUND_MAGENTA   = 0x0005
        FOREGROUND_YELLOW    = 0x0006
        FOREGROUND_GREY      = 0x0007
        FOREGROUND_INTENSITY = 0x0008 # foreground color is intensified.

        BACKGROUND_BLACK     = 0x0000
        BACKGROUND_BLUE      = 0x0010
        BACKGROUND_GREEN     = 0x0020
        BACKGROUND_CYAN      = 0x0030
        BACKGROUND_RED       = 0x0040
        BACKGROUND_MAGENTA   = 0x0050
        BACKGROUND_YELLOW    = 0x0060
        BACKGROUND_GREY      = 0x0070
        BACKGROUND_INTENSITY = 0x0080 # background color is intensified.     

        levelno = args[1].levelno
        if(levelno>=50):
            color = BACKGROUND_YELLOW | FOREGROUND_RED | FOREGROUND_INTENSITY | BACKGROUND_INTENSITY 
        elif(levelno>=40):
            color = FOREGROUND_RED | FOREGROUND_INTENSITY
        elif(levelno>=30):
            color = FOREGROUND_YELLOW | FOREGROUND_INTENSITY
        elif(levelno>=20):
            color = FOREGROUND_GREEN
        elif(levelno>=10):
            color = FOREGROUND_MAGENTA
        else:
            color =  FOREGROUND_WHITE
        args[0]._set_color(color)

        ret = fn(*args)
        args[0]._set_color( FOREGROUND_WHITE )
        #print "after"
        return ret
    return new

def add_coloring_to_emit_ansi(fn):
    # add methods we need to the class
    def new(*args):
        levelno = args[1].levelno
        if(levelno>=50):
            color = '\x1b[31m' # red
        elif(levelno>=40):
            color = '\x1b[31m' # red
        elif(levelno>=30):
            color = '\x1b[33m' # yellow
        elif(levelno>=20):
            color = '\x1b[32m' # green 
        elif(levelno>=10):
            color = '\x1b[35m' # pink
        else:
            color = '\x1b[0m' # normal
        args[1].msg = color + args[1].msg +  '\x1b[0m'  # normal
        #print "after"
        return fn(*args)
    return new

def set_logcolor():    
    import platform
    if platform.system()=='Windows':
        # Windows does not support ANSI escapes and we are using API calls to set the console color
        logging.StreamHandler.emit = add_coloring_to_emit_windows(logging.StreamHandler.emit)
    else:
        # all non-Windows platforms are supporting ANSI escapes so we use them
        logging.StreamHandler.emit = add_coloring_to_emit_ansi(logging.StreamHandler.emit)

   
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
hostname='20.0.0.10'

#base class, to provide basic ssh handler and interface
class FolderContainsBase(object):
    folder_contains_list=['unknown','tsc','db','mso']
    method_list=['do_nothing','prepare','backup','upload','invoke']
    folder_contains='unknown'
    local_dir = os.getcwd()

    #ctor, init ssh
    def __init__(self,name):
        self.set_folder_type(name)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname,22, 'root', password)
        self.channel = self.ssh.invoke_shell()
        log.warn(name+' installing now!!')

    #dtor, collect handle
    def __del__(self):
        pass
        #self.ssh.close()       
#-------interface for derived class------
    def prepare(self):
        pass        
    def do_nothing(self):
        pass
    def backup(self):
        pass
    def upload(self):
        pass
    def invoke(self):
        pass
#-------derived class implement end------

    def remove_back_slash(self,string):
        if string[-1] is '/':
            return string[:-1]

    #ssh.channel.send cmd wrapper
    def execute(self, cmd):
        cmd += '\r'
        tp = re.compile(r'@VOS:~# ')
        mp = re.compile(r'root@')
        while True:                   
            self.channel.send(cmd)
            time.sleep(0.5)
            result=''
            ret=self.channel.recv(65535)
            result+=str(ret)
            if tp.search(result) or mp.search(result) :
                #log.debug ("execute finished")
                break
    #get sudo prio
    def sudo(self):
        self.channel.send('sudo su\r')
        time.sleep(0.5)
        
    def killVOS(self):
        log.info('kill VOS instance to restart')
        cmd = 'kill `pgrep -n VOS.exe`'
        self.execute(cmd)
        time.sleep(0.5)

    def backupfolder(self,dst):
        cmd = 'mv ' + dst  + ' ' +self.remove_back_slash(dst)+ '-'+str(now)+'/'
        log.info(cmd)
        self.execute(cmd)
        time.sleep(0.5)
    #sftp wrapper, upload files
    def base_upload(self,local_dir,remote_dir):
        log.info('uploading...to ' + remote_dir+' '+' from '+local_dir)
        t=paramiko.Transport((hostname,port)) 
        t.connect(None,username,password)
        sftp=paramiko.SFTPClient.from_transport(t)

        log.info('upload file start  ' )
        for root,dirs,files in os.walk(local_dir):
            for filespath in files:
                local_file = os.path.join(root,filespath)
                a = local_file.replace(local_dir,'').replace('\\','/').lstrip('/')
                log.info('%s',  remote_dir)
                remote_file = os.path.join(remote_dir,a)
                log.info('%s',remote_file)
                try:
                    sftp.put(local_file,remote_file)
                    log.info('%s uploading',local_file)
                except Exception as e:
                    sftp.mkdir(os.path.split(remote_file)[0])
                    sftp.put(local_file,remote_file)
                    log.info("upload %s to remote %s" % (local_file,remote_file))
                    fh.close()
            for name in dirs: 
                local_path = os.path.join(root,name)
                log.info("%s,%s",local_path,local_dir)
                a = local_path.replace(local_dir,'').replace('\\','')
                remote_path = os.path.join(remote_dir,a)
                try:
                    sftp.mkdir(remote_path)
                    log.info("mkdir path %s" % remote_path)
                except Exception as e:
                    log.error("mkdir path %s" % remote_path)
                    
        log.info('upload file success  ' )
        
    def set_folder_type(self, name):
        self.folder_contains = name


class TscFiles(FolderContainsBase):
    script='tsc_config.sh'
    have_script=False
    def backup(self):
        self.sudo()
        log.info('TscFiles backup')
        self.backupfolder(remote_dir)

    def upload(self):
        log.info('TscFiles upload')
        self.base_upload(local_dir,remote_dir)
        
    def invoke(self):
        log.info('TscFiles invoke')
        if have_script:           
            self.killVOS()
        
    def prepare(self):
        if os.path.isfile(local_dir+"\\" + scripts) is False:
            log.info(u'请确保'+script +u'在文件夹下，否则无法修改配置文件')
        else:
            have_script=True


class MsoFiles(FolderContainsBase):
    script='mso_config.sh'
    have_script=False
    def backup(self):
        log.info('MsoFiles backup')
        self.backupfolder(remote_dir)
        
    def upload(self):
        self.base_upload(local_dir,remote_dir)
        log.info('MsoFiles upload')
        
    def invoke(self):
        self.killVOS()
        log.info('MsoFiles invoke')

    def prepare(self):
        if os.path.isfile(local_dir+"\\" + scripts) is False:
            log.info(u'请确保'+script +u'在文件夹下，否则无法修改配置文件')
        else:
            have_script=True
        
class DbFiles(FolderContainsBase):
    def backup(self):
        log.info('DbFiles backup')
        self.backupfolder(remote_db_dir)
        self.backupfolder(remote_path_dir)
        
    def upload(self):
        log.info('DbFiles upload')
        self.base_upload(local_dir,remote_db_dir)
        self.base_upload(local_remotepath_dir,remote_path_dir)
        
    def invoke(self):
        log.info('DbFiles invoke')
        #启动mysql
        log.info('-----start mysql-----')
        self.ssh.exec_command("/etc/init.d/services/mysql start")
        time.sleep(0.5)
        log.info('-----install db -----')
        std_in,std_out,_ = self.ssh.exec_command(\
            'cd ' +remote_db_dir+';\
            chmod 777 *;\
            dos2unix *;\
            ./setup_root;\
            ./setvariable;\
            ./setup_mso'\
            ,get_pty=True)
        std_in.write('all'+'\n')
        std_in.write('1'+'\n')
        log.info('----install message -----')
        for x in std_out.readlines():
            log.info(x.strip("\n"))

        
        self.ssh.exec_command(\
            'cd /opt/remotepath/;\
            chmod 777 *;\
            dos2unix hss_tsc;\
            dos2unix offline_bill')
        
    def prepare(self):
        log.info('DbFiles prepare')
        file_list = ["hss_tsc","sqlite3","offline_bill","tsc.db","my.cnf"]
        if os.path.exists(local_remotepath_dir) is False:
                os.mkdir(local_remotepath_dir)
                for f in file_list:
                        if os.path.isfile(local_dir+"\\" + f):
                                shutil.copyfile(local_dir+"\\" + f,local_remotepath_dir+"\\"+f)
                        else:
                                log.error("check "+f+" !! missing")
                                log.warn(u'请确保tsc.db在文件夹内，否则得你自己上传')
        
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

        self.prepare()
        self.backup()
        self.upload()
        self.invoke()

    def backup(self):
       self.instance.backup()

    def upload(self):
        self.instance.upload()
        
    def invoke(self):
        self.instance.invoke()

    def prepare(self):
        self.instance.prepare()


if __name__ == '__main__':
    print('-------------------------------------------')
    print("|           TSC  AutoDeploy               |")
    print('|                                         |')
    print('-------------------------------------------')
    print(u'请将该程序放在上传文件的同级目录下')
    print(u'程序会将同目录下所有文件上传，所以整准点')
    print(u'如果崩溃把日志rtx给w18858或者skype wangqw2ee@outlook.com')
    set_logcolor()
    hostname=input(u"ip (没有ip校验，别输错了):\n")

    key=input(u"密码 默认vos:\n")
    if key != '':
        password=key

    
    AutoDeploy()
    log.info ('complete %s' %now)
    time.sleep(60)
