#!/usr/bin/python3
#coding=utf-8

import paramiko
import os,sys
import logging
import re
import time
import shutil
import sqlite3
import configparser

now = time.strftime("%Y-%m-%d-%H-%M-%S")


##-------------conf file---------------------

CONFIG_STR = '''[COMM]
SERVER_IP = 20.0.2.2
[TSC]
TSC_ID = 1
MSO_IP = 20.0.2.2
DMR = 0

[MSO]
SystemID = 40706
DMR = 0
PSTN_IP = 20.0.2.73
CallMode = 3
DialPlan = 3
TSC1_ID =1
TSC1_IP = 20.0.0.2
TSC2_ID =2
TSC2_IP = 20.0.0.10
TSC3_ID =3
TSC3_IP = 20.0.0.18
'''

# gen AutoDeploy.ini in this folder
def get_config_file():
    full_name = os.getcwd() + '\\' + 'AutoDeploy.ini'
    if not os.path.isfile(full_name):
        conf = open(full_name,'w')
        conf.write(CONFIG_STR)
        conf.close()


##--------------log color--------------------
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
ch.setLevel(logging.INFO)
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
                log.debug ("execute finished")
                break
            
    #get sudo prio
    def sudo(self):
        self.channel.send('sudo su\r')
        time.sleep(0.5)

    def chmod(self):
        cmd = 'chmod 777 ' + remote_dir+'*'
        log.info(cmd)
        self.execute(cmd)
        '''_,std_out,_ = self.ssh.exec_command('sudo su;'+cmd)
        for x in std_out.readlines():
            log.info(x.strip("\n"))'''
        time.sleep(0.5)
        
    def killVOS(self):
        cmd = 'kill `pgrep -n VOS.exe`'
        log.info(cmd)
        self.execute(cmd)
        '''_,std_out,_ =self.ssh.exec_command('sudo su;'+cmd,get_pty=True)
        for x in std_out.readlines():
            log.info(x.strip("\n"))'''
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
                log.debug('%s',  remote_dir)
                remote_file = os.path.join(remote_dir,a)
                log.debug('%s',remote_file)
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
                log.debug("%s,%s",local_path,local_dir)
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
    def backup(self):
        self.sudo()
        log.info('TscFiles backup')
        self.backupfolder(remote_dir)

    def upload(self):
        log.info('TscFiles upload')
        self.base_upload(local_dir,remote_dir)
        
    def invoke(self):
        self.sudo()
        log.info('TscFiles invoke')
        self.chmod()
        self.killVOS()
        shutil.copyfile(self.db_dir,self.db_dir+hostname+'.db')
        shutil.copyfile(self.db_dir+".bak",self.db_dir)

    #config db file        
    def prepare(self):
        TSC_IP = hostname
        log.info('TscFile prepare....Config db....')
        db='VOS.Config.db'
        db_ver1 = local_dir+'\\'+db
        db_ver2 = local_dir+'\\'+'data'+'\\'+db
        conf=local_dir+'\\'+'AutoDeploy.ini'
        if os.path.isfile(db_ver1):
            log.warn('db file is '+db_ver1)
            self.db_dir=db_ver1            
        elif os.path.isfile(db_ver2):
            log.warn('db file is '+db_ver2)
            self.db_dir=db_ver2
        else:
            log.error('where is db file????')
            time.sleep(600)
            quit(-1)

        conn=sqlite3.connect(self.db_dir)
        shutil.copyfile(self.db_dir,self.db_dir+".bak")
        config=configparser.ConfigParser()
        try:
            config.read(conf)
            TSC_ID=config.get('TSC','TSC_ID')
            MSO_IP=config.get('TSC','MSO_IP')
            DMR=config.get('TSC','DMR')
        except:
            log.error(u'注意AutoDeploy.ini文件必须保存为utf8无bom文件，请用notepad++操作，而不是使用Windows自带的notepad (win10notepad1803解决了这个问题)')
            log.info(u'或者你可以按照提示手动输入需要配置的信息(参数无校验)')
            TSC_ID=input(u"基站的网元编号(TSC_ID):\n")
            MSO_IP=input(u"基站归属中控的ip:\n")
            DMR= input("DmrCmpMode:\n")
        finally:
            log.info('tsc_ip=%s,tsc_id=%s,mso_ip=%s,dmr=%s', TSC_IP ,TSC_ID ,MSO_IP ,DMR)

        sqlstr='''
insert or replace into Tbl_Config (PID,Tag,Key,Value,Comment) VALUES(0,"VOS", "LOGVIEW/MAXCOUNT","10","");
update Tbl_Config set Value='0xff004f1f' where Tag='VOS' and Key='LOG/LOGLEVEL';
update Tbl_Config set Value='2/true/$TSC_IP:8000/$MSO_IP:6088' where Tag='VOS/SERVICES/IServices/TRT'  and Key='23:0';
update Tbl_Config set Value='2/true/$TSC_IP:8002/$MSO_IP:5002' where Tag='VOS/SERVICES/IServices/TRT' and Key='36:28672';
/*TSC 修改*/
update Tbl_Config set Value='$TSC_ID'          where  Tag='TSC'and Key='TSC_ID';
update Tbl_Config set Value='$DMR'           where  Tag='TSC'and Key='DMRCmptMode';
update Tbl_Config set Value='$TSC_IP:0' where  Tag='TSC'and Key='TSC_ExtraNetIP';
/* Agent 配置修改*/
update Tbl_Config set Value='$MSO_IP' where  Tag='Agent'and Key='OM_SERVER_IP';
update Tbl_Config set Value='$MSO_IP' where  Tag='Agent'and Key='OM_SLAVE_IP';
update Tbl_Config set Value='$TSC_IP'  where  Tag='Agent'and Key='AGENT_IP';
update Tbl_Config set Value='$TSC_ID'        where  Tag='Agent'and Key='TSC_ID';
'''
        sqlstr=sqlstr.replace('$MSO_IP',MSO_IP)
        sqlstr=sqlstr.replace('$TSC_IP',TSC_IP)
        sqlstr=sqlstr.replace('$TSC_ID',TSC_ID)
        sqlstr=sqlstr.replace('$DMR',DMR)
        
        conn.executescript(sqlstr)
        conn.commit()
        conn.close()
        
        
class MsoFiles(FolderContainsBase):
    def backup(self):
        log.info('MsoFiles backup')
        self.backupfolder(remote_dir)
        
    def upload(self):
        log.info('MsoFiles upload')
        self.base_upload(local_dir,remote_dir)        
        
    def invoke(self):        
        log.info('MsoFiles invoke')
        self.chmod()
        self.killVOS()
        shutil.copyfile(self.db_dir,self.db_dir+hostname+'.db')
        shutil.copyfile(self.db_dir+".bak",self.db_dir)

    def prepare(self):
        MSO_IP = hostname
        log.info('MSO File prepare....Config db....')
        db='VOS.Config.db'
        db_ver1 = local_dir+'\\'+db
        db_ver2 = local_dir+'\\'+'data'+'\\'+db
        conf=local_dir+'\\'+'AutoDeploy.ini'
        if os.path.isfile(db_ver1):
            log.warn('db file is '+db_ver1)
            self.db_dir=db_ver1
        elif os.path.isfile(db_ver2):
            log.warn('db file is '+db_ver2)
            self.db_dir=db_ver2
        else:
            log.error('where is db file????')
            time.sleep(600)
            quit(-1)

        shutil.copyfile(self.db_dir,self.db_dir+".bak")
        conn=sqlite3.connect(self.db_dir)
        c=conn.cursor()
        OLD_MSO_IP = c.execute("select Value from Tbl_Config  where  Tag='VOS/SERVICES/IServices/CRT'and Key='51:0x3000'")\
                     .fetchone()[0].split('/')[-1].split(':')[0]
        #('0/false/20.0.2.178:6088/20.0.2.178:8088',)
        c.close()
        
        config=configparser.ConfigParser()
        try:
            config.read(conf)
            SystemID=config.get('MSO','SystemID')
            PSTN_IP=config.get('MSO','PSTN_IP')
            DMR=config.get('MSO','DMR')
            CallMode=config.get('MSO','CallMode')
            DialPlan=config.get('MSO','DialPlan')
            TSC1_IP=config.get('MSO','TSC1_IP')
            TSC2_IP=config.get('MSO','TSC2_IP')
            TSC3_IP=config.get('MSO','TSC3_IP')
            TSC1_ID=config.get('MSO','TSC1_ID')
            TSC2_ID=config.get('MSO','TSC2_ID')
            TSC3_ID=config.get('MSO','TSC3_ID')
        except:
            log.error(u'注意AutoDeploy.ini文件必须保存为utf8无bom文件，请用notepad++操作，而不是使用Windows自带的记事本 (win10 1803解决了这个问题)')
            log.info(u'或者你可以按照提示手动输入需要配置的信息(参数无校验)')
            SystemID=input(u"中控的SystemID:\n")
            DMR= input("DmrCmpMode [1:DMR][0:PDT]:\n")
            PSTN_IP=input("PSTN_IP:\n")
            CallMode=input("CallMode? [4:DMR][3:PDT-P3][8:MPT&DMR]:\n")
            DialPlan=input("Dial Plan [3,4,5,6,8] :\n")
            TSC1_ID=input("TSC1_ID:\n")
            TSC1_IP=input("TSC1_IP:\n")
            TSC2_ID=input("TSC2_ID:\n")
            TSC2_IP=input("TSC2_IP:\n")
            TSC3_ID=input("TSC3_ID:\n")
            TSC3_IP=input("TSC3_IP:\n")
        finally:
            pass
            #log.info('MSO_IP=%,SystemID=%s,DMR=%s,PSTN_IP=%s,CallMode=%s，DialPlan=%s,TSC1_IP=%s,TSC2_IP=%s,TSC3_IP=%s' ,MSO_IP ,SystemID ,DMR ,PSTN_IP ,CallMode ,DialPlan ,TSC1_IP ,TSC2_IP ,TSC3_IP)
        
        sqlstr='''
/*Log counts*/
insert or replace INTO Tbl_Config (PID,Tag,Key,Value,Comment) VALUES(0,"VOS", "LOGVIEW/MAXCOUNT","10","");
update Tbl_Config set value = replace (value,'$OLD_MSO_IP','$MSO_IP');
/*PSTN*/
update Tbl_Config set Value='$PSTN_IP:5060'           where  Tag='PSTNGW'and Key='PSTNIp';
/*MTU*/
update Tbl_Config set Value='1/false/0.0.0.0:7000/20.0.2.130:6080'           where  Tag='VOS/SERVICES/IServices/CRT'and Key='60:0x6000';
/*system id*/
update Tbl_Config set Value='$SystemID'           where  Tag='MSO'and Key='SystemID';
/* DMR */
update Tbl_Config set Value='$DMR'           where  Tag='MSO'and Key='DMRCmptMode';
/* Call Mode*/
update Tbl_Config set Value='$CallMode'      where  Tag='SAG' and Key='SYS_MODE';
/* Dial Plan 6.5*/
update Tbl_Config set Value='$DialPlan'	where Tag='MSO' and Key='DialPlan';
/*SAG*/
update Tbl_Config set value = replace (value,'192.168.20.96','$MSO_IP');
/*SPGP*/
update Tbl_Config set value = replace (value,'192.168.20.18','$MSO_IP');
update Tbl_Config set value="$MSO_IP:6000" where tag = "SPGP" and key = "MsoIp";
/*AISGW*/
update Tbl_Config set value="$MSO_IP:5062" where tag = "AISGW" and key = "AISGWIP";
/*GPSS*/
update Tbl_Config set value="2/false/$MSO_IP:29876/$MSO_IP:0" where tag = "VOS/SERVICES/IServices/GPSS" and key = "56";
/*vauc*/
update Tbl_Config set value="2/false/$MSO_IP:5002/$MSO_IP:8002" where tag = "VOS/SERVICES/IServices/V_AuC" and key = "4";
update Tbl_Config set value="$MSO_IP:3696" where tag = "V_AuC" and key = "AucUDPAddr";
update Tbl_Config set value="$MSO_IP:5500" where tag = "V_AuC" and key = "KdmcUDPAddr";
update Tbl_Config set value="$MSO_IP:3696" where tag = "V_AuC" and key = "LocalUDPAddr";
update Tbl_Config set value="2/false/$MSO_IP:6088/$TSC1_IP:8000" where tag = "VOS/SERVICES/IServices/CRT" and key = "4:1";
update Tbl_Config set key="4:$TSC1_ID" where tag = "VOS/SERVICES/IServices/CRT" and value = "2/false/$MSO_IP:6088/$TSC1_IP:8000";
update Tbl_Config set value="2/false/$MSO_IP:6088/$TSC2_IP:8000" where tag = "VOS/SERVICES/IServices/CRT" and key = "4:2";
update Tbl_Config set key="4:$TSC2_ID" where tag = "VOS/SERVICES/IServices/CRT" and value = "2/false/$MSO_IP:6088/$TSC2_IP:8000";
update Tbl_Config set value="2/false/$MSO_IP:6088/$TSC3_IP:8000" where tag = "VOS/SERVICES/IServices/CRT" and key = "4:3";
update Tbl_Config set key="4:$TSC3_ID" where tag = "VOS/SERVICES/IServices/CRT" and value = "2/false/$MSO_IP:6088/$TSC3_IP:8000";
--replace INTO Tbl_Config (PID,Tag,Key,Value,Comment) VALUES(0,"VOS/SERVICES/IServices/CRT", "4:$TSC_ID", "2/false/$MSO_IP:6088/$TSC_IP:8000","");
'''

        sqlstr=sqlstr.replace('$OLD_MSO_IP',OLD_MSO_IP)
        sqlstr=sqlstr.replace('$MSO_IP',MSO_IP)
        sqlstr=sqlstr.replace('$SystemID',SystemID)
        sqlstr=sqlstr.replace('$DMR',DMR)
        sqlstr=sqlstr.replace('$PSTN_IP',PSTN_IP)
        sqlstr=sqlstr.replace('$CallMode',CallMode)
        sqlstr=sqlstr.replace('$DialPlan',DialPlan)
        sqlstr=sqlstr.replace('$TSC1_IP',TSC1_IP)
        sqlstr=sqlstr.replace('$TSC2_IP',TSC2_IP)
        sqlstr=sqlstr.replace('$TSC3_IP',TSC3_IP)
        sqlstr=sqlstr.replace('$TSC1_ID',TSC1_ID)
        sqlstr=sqlstr.replace('$TSC2_ID',TSC2_ID)
        sqlstr=sqlstr.replace('$TSC3_ID',TSC3_ID)
        #log.info(sqlstr)
        conn.executescript(sqlstr)
        conn.commit()
        conn.close()
    
class DbFiles(FolderContainsBase):

    db_backup_dir = '/opt/local/bin/VOS/db/db_backup/'
    db_install_dir = remote_db_dir

    def backup_db(self):
        log.info('-----backup db -----')
        std_in,std_out,_ =self.ssh.exec_command(\
            'cp ' +self.db_install_dir + 'backup_* '+ self.db_backup_dir+'; \
            cp - r '+self.db_install_dir+'statistic/ ' + self.db_backup_dir+'; \
            cp ' + self.db_install_dir+'delete_back_up ' + self.db_backup_dir+'; \
            chmod 777 '+self.db_backup_dir+'*;\
            dos2unix '+self.db_backup_dir+'backup_*;\
            dos2unix '+self.db_backup_dir+'delete_backup;\
            dos2unix '+self.db_backup_dir+'statistic/*')
        for x in std_out.readlines():
            log.info(x.strip("\n"))

    def install_db(self):
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
        self.backup_db()
        time.sleep(0.5)
        self.install_db()
        time.sleep(0.5)
        
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
    print("|                AutoDeploy               |")
    print('|                                         |')
    print('-------------------------------------------')
    print(u'请将该程序放在上传文件的同级目录下')
    print(u'如果是TSC文件或MSO文件请确保AutoDeploy.ini内容配置正确')
    print(u'如果闪退把日志rtx:w18858 Or skype:wangqw2ee@outlook.com')
    set_logcolor()
    get_config_file()
    t_start=time.time()
	
    config=configparser.ConfigParser()
    try:
        config.read('AutoDeploy.ini')
        hostname=config.get('COMM','SERVER_IP')
    except:
        log.error(u'注意AutoDeploy.ini文件必须保存为utf8无bom文件，请用notepad++操作，而不是使用Windows自带的notepad (win10notepad1803解决了这个问题)')
        log.info(u'或者没有AutoDeploy.ini文件，没关系，你可以按照提示手动输入需要配置的信息(参数无校验)')
    finally:
        hostname_in=input(u"ip (没有ip校验，别输错了) 回车默认 %s:\n" %hostname)  
        if hostname_in != '':
            hostname = hostname_in

    key=input(u"密码 回车默认vos:\n")
    if key != '':
        password=key
    
    AutoDeploy()
    t_end=time.time()
    
    log.info ('complete %s, all cost %d seconds' ,now ,(t_end-t_start))
    time.sleep(6000)
