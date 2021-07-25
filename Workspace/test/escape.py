# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 26-06-2021 14:43:04
 LastEditors: Yichen Zhang
 LastEditTime: 27-06-2021 17:21:14
 FilePath: /circuit/Workspace/test/escape.py
'''
import os

os.chdir(os.path.dirname(__file__))
with open('temp') as f,open('str','w') as ff:
    file=f.read()
    # print(file)
    # ff.write(file.encode('unicode_escape').decode('ASCII'))
    ff.write(file)
    loc=ff.tell()
    ff.write('rwgdbdr\nqrgdbgrt\nwrhthwg\nq4regss\nrsdg\nweragfdsr\n')

with open('str','r+') as ff:
    ff.seek(loc)
    ff.truncate()
    ff.write('\n.control\n\t options\n\n.endc\n')
