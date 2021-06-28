# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 28-06-2021 14:37:12
 LastEditors: Yichen Zhang
 LastEditTime: 28-06-2021 20:03:12
 FilePath: /circuit/Workspace/clear.py
'''
import os
import shutil

os.chdir(os.path.dirname(os.path.abspath(__file__)))
pt=[f.path for f in os.scandir() if f.is_dir()]
for item in ['./include', './share', './test', './bin', './lib']:
    pt.remove(item)
if not pt:
    print('Nothing Deleted')
else:
    for item in pt:
        shutil.rmtree(item)
        print(f"Deleted Folder '{item}'")
'''
p=os.listdir()
for item in ['bin','include','lib','share','test',os.path.basename(__file__)]:
    p.remove(item)
if not p:
    print('Nothing Deleted')
else:
    for item in p:
        shutil.rmtree(item)
        print(f"Deleted Folder '{item}'")
'''