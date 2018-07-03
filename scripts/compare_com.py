#!/usr/bin/python
# coding=utf-8

#compare
import filecmp
import shutil

from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter import messagebox

root = Tk()
path_local = StringVar()
path_comm = StringVar()

def select_local_path():
    path_ = askdirectory()
    path_local.set(path_)

def select_comm_path():
    path_ = askdirectory()
    path_comm.set(path_)

#补充反斜杠
def add_black_slash(s):
    if s[-1] is not '/' :
        s = s + '/'
    return s



def dif_file_str(com_dir,lo_dir,l):
    if len(l):
        res= u"在目录"+ lo_dir+u"下，以下文件和目录下"+com_dir+u" 的文件不一致 \n"
        for s in l:
          res+=s;
          res+="\n"
        return res
    else:
        return ""


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

def compare_comm(common_d,local_d,merge_flag=False):
    #1
    ans=""
    TSC_MSO_Common = common_d+'TSC_MSO_Common/'
    TSC_MSO_H = local_d+'TSC_MSO_H/'
    dif = filecmp.cmpfiles(TSC_MSO_Common,TSC_MSO_H,['PDTHead.h','TSC_MSO_Common.h'])
    ans+=dif_file_str(TSC_MSO_Common,TSC_MSO_H,dif[1])
    if merge_flag is True:
        for d in dif[1]:
            shutil.copyfile(TSC_MSO_Common+d,TSC_MSO_H+d)
    
    #2
    NM_Common = common_d+'NM_Common/'
    OM_H = local_d+'OM_H/'
    d = filecmp.dircmp(NM_Common,OM_H)
    ans+=dif_file_str(NM_Common,OM_H,d.diff_files)
    if merge_flag is True:
        for d_ in d.diff_files:
            shutil.copyfile(NM_Common+d_,OM_H+d_)

    #3
    OTAR_Common = common_d+'OTAR_Common/'
    TSC_BRS_H = local_d+'TSC_BRS_H/'
    CTSC_BRS_H = common_d+'TSC_BRS_H/'
    dif = filecmp.cmpfiles(OTAR_Common,TSC_BRS_H,['OTAR.h'])
    ans+=dif_file_str(OTAR_Common,TSC_BRS_H,dif[1])
    if merge_flag is True:
        for d in dif[1]:
            shutil.copyfile(OTAR_Common+d,TSC_BRS_H+d)

    dif = filecmp.cmpfiles(CTSC_BRS_H,TSC_BRS_H,["TSC_BRS.h"])
    ans+=dif_file_str(CTSC_BRS_H,TSC_BRS_H,dif[1])
    if merge_flag is True:
        for d in dif[1]:
            shutil.copyfile(CTSC_BRS_H+d,TSC_BRS_H+d)
    
    #4
    Auc_Common = common_d+'Auc_Common/'
    dif = filecmp.cmpfiles(Auc_Common,TSC_MSO_H,['Common_V_AuC.h'])
    ans+=dif_file_str(Auc_Common,TSC_MSO_H,dif[1])
    if merge_flag is True:
        for d in dif[1]:
            shutil.copyfile(Auc_Common+d,TSC_MSO_H+d)

    #5
    PDU = common_d+'PDU/'
    COMM_H = local_d+'COMM_H/'
    dif = filecmp.cmpfiles(PDU,COMM_H,['CCL_PDU.h','Common_Info.h'])
    ans+=dif_file_str(PDU,COMM_H,dif[1])
    if merge_flag is True:
        for d in dif[1]:
            shutil.copyfile(PDU+d,COMM_H+d)

    #6
    Common_Type = common_d+'Common_Type/'
    dif = filecmp.cmpfiles(Common_Type,COMM_H,['Common_Type.h'])
    ans+=dif_file_str(Common_Type,COMM_H,dif[1])
    if merge_flag is True:
        for d in dif[1]:
            shutil.copyfile(Common_Type+d,COMM_H+d)

    if len(ans)==0:
        ans="没有不同"
    messagebox.showinfo("比对结果",ans)
    
        

     
def compare(merge_flag=False):
    common_dir = path_comm.get()
    common_dir = add_black_slash(common_dir)
    local_dir = path_local.get()
    local_dir = add_black_slash(local_dir)
    try:
        compare_comm(common_dir,local_dir,merge_flag)
    except:
       messagebox.showwarning('警告',"文件目录是否正确？")
    finally:
        pass

def merge():
    compare(True)
        
root.title("TSC头文件比对")
Label(root,text = "本地头文件路径").grid(row=0,column=0)
Label(root,text = "公共头文件路径").grid(row=1,column=0)
Entry(root,textvariable=path_local).grid(row=0,column=1)
Entry(root,textvariable=path_comm).grid(row=1,column=1)
Button(root,text="选择路径",command = select_local_path).grid(row=0,column=2)
Button(root,text="选择路径",command = select_comm_path).grid(row=1,column=2)
Button(root,text="比对",command = compare).grid(row=0,column=3)
Button(root,text="合并",command = merge).grid(row=1,column=3)
root.mainloop()






    


    
