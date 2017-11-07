#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys
import os
import comtypes.client


wdFormatPDF = 17

filepath = os.path.abspath(os.getcwd())

filelist = os.listdir(filepath)

for i in range (0,len(filelist)):
	if 'doc' in filelist[i] or 'DOC'in filelist[i] :
		if	'~$' not in filelist[i]:
			f = os.path.join(filepath,filelist[i])
			print(f)
			if os.path.isfile(f):
				print(f)
				word = comtypes.client.CreateObject('Word.Application')
				doc = word.Documents.Open(f)
				#print(os.getcwd()+'\\'+ filelist[i]+'.pdf')
				doc.SaveAs(os.getcwd()+'\\'+ filelist[i]+'.pdf', FileFormat=wdFormatPDF)
				doc.Close()
				word.Quit()
