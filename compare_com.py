#!/usr/bin/python
# coding=utf-8
#   头文件比对工具,头文件太TM乱了
#   使用方法 path.ini里写好common头文件和本地头文件目录，点击执行

#parser ini
import configparser
config=configparser.ConfigParser()
config.read('path.ini','utf-8')
common_dir = config.get('common','dir')
local_dir = config.get('local','dir')

#compare
import filecmp

#pause
import time

#补充反斜杠
def add_black_slash(s):
    if s[-1] is not '\\' :
        s = s + '\\'
    return s

common_dir = add_black_slash(common_dir)
local_dir = add_black_slash(local_dir)

#通用打印
#TODO 内部记录状态，闭包
def print_file_list(com_dir,lo_dir,l):
    if len(l):
        print(u"在目录", lo_dir,u"下，以下文件和目录下",com_dir,u" 的文件不一致")
        print(l)
        print("")
    

'''
+----------------+-------------+
|    common      |    local    |
|TSC_MSO_Common  |  TSC_MSO_H  |
| NM_Common      |	OM_H   |
| OTAR_Common	 |  TSC_BRS_H  |
|  PDU		 |	COMM_H |
| Common_Type    |  COMM_H     |
| Auc_Common     | TSC_MSO_H   |
+----------------+-------------+
'''

#hardcode! 遍历 common目录，来比较本地目录下文件是否不同

def compare_comm(common_d,local_d):
    #1
    TSC_MSO_Common = common_d+'TSC_MSO_Common\\'
    TSC_MSO_H = local_d+'TSC_MSO_H\\'
    dif = filecmp.cmpfiles(TSC_MSO_Common,TSC_MSO_H,['PDTHead.h','TSC_MSO_Common.h'])
    print_file_list(TSC_MSO_Common,TSC_MSO_H,dif[1])
    
    #2
    NM_Common = common_d+'NM_Common\\'
    OM_H = local_d+'OM_H\\'
    d = filecmp.dircmp(NM_Common,OM_H)
    print_file_list(NM_Common,OM_H,d.diff_files)


    #3
    OTAR_Common = common_d+'OTAR_Common\\'
    TSC_BRS_H = local_d+'TSC_BRS_H\\'
    CTSC_BRS_H = common_d+'TSC_BRS_H\\'
    dif = filecmp.cmpfiles(OTAR_Common,TSC_BRS_H,['OTAR.h'])
    print_file_list(OTAR_Common,TSC_BRS_H,dif[1])

    dif = filecmp.cmpfiles(CTSC_BRS_H,TSC_BRS_H,["TSC_BRS.h"])
    print_file_list(CTSC_BRS_H,TSC_BRS_H,dif[1])
    
    #4
    Auc_Common = common_d+'Auc_Common\\'
    dif = filecmp.cmpfiles(Auc_Common,TSC_MSO_H,['Common_V_AuC.h'])
    print_file_list(Auc_Common,TSC_MSO_H,dif[1])

    #5
    PDU = common_d+'PDU\\'
    COMM_H = local_d+'COMM_H\\'
    dif = filecmp.cmpfiles(PDU,COMM_H,['CCL_PDU.h','Common_Info.h'])
    print_file_list(PDU,COMM_H,dif[1])

    #6
    Common_Type = common_d+'Common_Type\\'
    dif = filecmp.cmpfiles(Common_Type,COMM_H,['Common_Type.h'])
    print_file_list(Common_Type,COMM_H,dif[1])

     

if __name__ == "__main__":
    print(u'------TSC头文件比对工具--------')
    print(u'确保以下目录是正确的：')
    print (u'    公共头文件目录: ',common_dir)
    print (u'    本地common目录: ',local_dir)
    print ("")

    print(u"比对开始！")
    compare_comm(common_dir,local_dir)
    print(u"比对结束！")

    time.sleep(600)
    


    
