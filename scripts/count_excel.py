import xlrd
<<<<<<< HEAD
data = xlrd.open_workbook(r"C:\Users\Administrator\Desktop\xxx.xls")
=======
data = xlrd.open_workbook(r"C:\Users\Administrator\Desktop\R5.0联调用例.xls")
>>>>>>> 20fc19f4f75155c0a2627380883030bcd2c9a215
s = 0;
for i in range(len(data.sheets())):
    table = data.sheets()[i]
    s = s+table.nrows -1

print(s)
