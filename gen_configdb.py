#!/usr/bin/python
# coding=utf-8
import sqlite3
connect = sqlite3.connect('VOS.Config.db')
sql = open('VOS.Config.db.sql',"r+")
sqlstr = sql.read()
sql.close()
print("db executescript begin")
connect.executescript(sqlstr)
connect.commit()
connect.execute("VACUUM")
connect.close()
print("db executescript end")
