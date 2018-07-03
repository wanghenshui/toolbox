import xlrd
data = xlrd.open_workbook(r"C:\Users\Administrator\Desktop\R5.0联调用例.xls")
s = 0;
for i in range(len(data.sheets())):
    table = data.sheets()[i]
    s = s+table.nrows -1

print(s)
