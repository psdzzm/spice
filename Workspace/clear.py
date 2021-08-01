# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description: Delete the folders that have been uploaded
 Author: Yichen Zhang
 Date: 28-06-2021 14:37:12
 LastEditors: Yichen Zhang
 LastEditTime: 01-08-2021 23:41:12
 FilePath: /spice/Workspace/clear.py
'''
import os
import shutil

os.chdir(os.path.dirname(os.path.abspath(__file__)))
pt = [f.path for f in os.scandir() if f.is_dir()]
for item in ['./include', './share', './test', './bin', './lib']:
    pt.remove(item)
if not pt:
    print('Nothing Deleted')
else:
    for item in pt:
        shutil.rmtree(item)
        print(f"Deleted Folder '{item}'")
