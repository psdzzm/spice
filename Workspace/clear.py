# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description: Delete the folders that have been uploaded
 Author: Yichen Zhang
 Date: 28-06-2021 14:37:12
 LastEditors: Yichen Zhang
 LastEditTime: 07-08-2021 21:48:45
 FilePath: /spice/Workspace/clear.py
'''
import os
import shutil

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Delete user uploaded netlists
for item in [f.path for f in os.scandir() if f.is_dir() and f.path not in ['./include', './share', './test', './bin', './lib']]:
    shutil.rmtree(item)
    print(f"Deleted Folder '{item}'")

# Delete user uploaded subcircuit files
if os.path.isdir('lib/user'):
    shutil.rmtree('lib/user')
    print(f"Deleted all files in 'Workspace/lib/user'")
else:
    print('Nothing Deleted')

# Make folder
os.mkdir('lib/user')
