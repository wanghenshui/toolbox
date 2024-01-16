import xlrd
from tkinter import *
from tkinter.filedialog import askdirectory,askopenfilename
from tkinter import messagebox

root = Tk()
path = StringVar()

def select_path():
    path_ = askopenfilename()
    path.set(path_)

def count_excel():
    try:
        data = xlrd.open_workbook(path.get())
        s = 0;
        for i in range(len(data.sheets())):
            table = data.sheets()[i]
            s = s+table.nrows -1
            #print(s)
        messagebox.showinfo('总行数 ',s)
    except Exception as e:        
        messagebox.showwarning('警告',"文件是否正确？")
        messagebox.showwarning('警告',e)
    finally:
        pass
        
root.title("count excel")
Label(root,text = "Excel路径").grid(row=0,column=0)
Entry(root,textvariable=path).grid(row=0,column=1)
Button(root,text="选择文件路径",command = select_path).grid(row=0,column=2)
Button(root,text="计算",command = count_excel).grid(row=0,column=3)
root.mainloop()
