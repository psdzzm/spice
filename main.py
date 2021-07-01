# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 26-06-2021 14:43:04
 LastEditors: Yichen Zhang
 LastEditTime: 01-07-2021 18:23:01
 FilePath: /circuit/main.py
'''

from src.plot import plotGUI
from PyQt5 import QtWidgets
import os,sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
root=os.getcwd()
path=root+'/Workspace/bin'
if path not in os.environ['PATH']:
    os.environ['PATH']+=':'+path
del path

print(os.environ['PATH'])

app = QtWidgets.QApplication(sys.argv)
main = plotGUI(root)
main.show()
app.exec_()
print(os.getcwd())