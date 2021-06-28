# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 28-06-2021 14:37:12
 LastEditors: Yichen Zhang
 LastEditTime: 28-06-2021 15:27:00
 FilePath: /circuit/Workspace/clear.py
'''
import os
import shutil

os.chdir(os.path.dirname(__file__))
pp=[f.path for f in os.scandir() if f.is_dir()]
p=os.listdir()
for item in ['bin','include','lib','share','test',os.path.basename(__file__)]:
    p.remove(item)
if not p:
    print('Nothing Deleted')
else:
    for item in p:
        shutil.rmtree(item)
        print(f"Deleted Folder '{item}'")