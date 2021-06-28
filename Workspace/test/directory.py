# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 26-06-2021 14:43:04
 LastEditors: Yichen Zhang
 LastEditTime: 28-06-2021 12:19:29
 FilePath: /circuit/Workspace/test/directory.py
'''
import os
import shutil
import subprocess
from datetime import datetime
import numpy as np

# path=os.getcwd()+'/Workspace/bin'
# os.environ['PATH']+=':'+path
# print(os.environ['PATH'])
# os.system('ngspice')
home=os.path.expanduser('~')

os.chdir(os.path.dirname(__file__))
print(os.getcwd())
x=np.zeros([2,5],dtype=np.complex_)
for j in range(5):
    x[0,j]= 1 + (0 if not j else j)*1j
print(x)
x=np.log10(np.abs(x))*20
print(x)

x=['aa','bb','cc','bb','cc']
index=[i for i, x in enumerate(x) if x == "bb"]
index=[index]
index.append([i for i, x in enumerate(x) if x == "cc"])
print(index)

str0='out of asrshgf q4ierjdsg fgvf freq df abc dd qtrewfgew'
if 'abc dd' in str0:
    print('exist')
else:
    print('not found')

# os.chdir('Workspace/')
# os.chdir('..')
# print(os.getcwd())
# dir='Workspace/'+datetime.now().strftime("%d%m%Y_%H%M%S")+'/'
# os.mkdir(dir)
# shutil.copyfile('main.py',dir+'main')
# print(os.path.isfile('test/main'))
'''
with open('test.cir','r+') as a:
    text=a.read()
    text=text.replace('include','.inc')
    print(text)
'''

# proc=subprocess.Popen('ngspice -b test.cir -o test.log',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
# proc=subprocess.Popen('ngspice -b test.cir -o test.log',shell=True,stderr=subprocess.PIPE)
# _,stderr=proc.communicate()
# stderr=stderr.decode('ASCII')
# print(proc.returncode)
# # print('STDOUT: ',stdout)
# print('STDERR: ',stderr.encode('unicode_escape').decode('ASCII'),type(stderr))
# if stderr:
#     print('Something')