#!/usr/bin/python
# coding=utf-8

class configfile:
    import configparser
    import os
    file_name = os.getcwd() + '\\' + 'ntp_tool.ini'

    def __doc__(self):
        '''
        configfile class
        configparser的封装，负责解析出ip列表，或者获取用户输入的ip
        '''
    def detail(self):
        return '''[IP]
MASTER = 20.0.2.2
SLAVE = 20.0.0.10,20.0.0.26,20.0.0.58'''
    
    def is_conf_exist(self):
        return self.os.path.isfile(self.file_name)
    
    def __init__(self):
        if self.is_conf_exist() is not True:
            f = open(self.file_name,'w')
            f.write(self.detail())
            f.close()

    def load(self):
        try:
            conf = self.configparser.ConfigParser()
            conf.read(self.file_name)
            m=conf.get('IP','MASTER')
            s=conf.get('IP','SLAVE')
            l=s.split(',')
            l.insert(0,m)
            return l
        except Exception as e:
            raise 
            

    def input_ip_list(self):
        try:
            s= input(u'请输入一串IP以逗号,分割 第一个是中心IP其余的ip是受同步的ip: ')
            return s.split(',')
            #['0.0.0.0','0.0.0.0','2.2.2.2']
        except:
            pass
        finally:
            quit(1)
            
    def iplist(self):
        ans = input(u'请确认读取配置文件(请确保ini文件已经修改)还是手动输入[Y/n]')
        if ans in ['' ,'y' ,'Y']:
            try:
                l=self.load()
            except:
                print(u'配置文件解析失败，可能是格式问题')
                l = self.input_ip_list()
            finally:
                return l            
        else:
            return self.input_ip_list()
            
            
        

class ntp_tool:
    import paramiko
    import re
    iplist=[]#解析配置文件或用户传入
    ntpc=[]#ntp client 需要连入查看ntp状态
    ntps=''#ntp server 用于检查
    def info(self):
        '''
        ntp tool
        继承配置解析与SSH
            调用run执行
        '''
        print('NTP Tool: Check NTP and Auto Just.')
        
        
    def __init__(self):
        self.info() 
        self.conf = configfile()
        self.iplist = self.conf.iplist()
        self.ssh = self.paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(self.paramiko.AutoAddPolicy())        
 
        
    def run(self):
        if len(self.iplist)>2:
            self.ntps = self.iplist[0]
            self.ntpc = self.iplist[1:]
            for ip in ntpc:
                try:
                    print(ip,' connecting')
                    #self.ssh.connect(ip,22,'root','vos')
                    #self.ssh_channel = self.ssh.invoke_shell()
                except:
                    print(ip,u' 连接连接失败，请手动同步')
        


if __name__ == '__main__':
    NTP = ntp_tool()
    NTP.run()
