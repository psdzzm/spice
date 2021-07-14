# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 26-06-2021 14:43:04
 LastEditors: Yichen Zhang
 LastEditTime: 14-07-2021 01:29:05
 FilePath: /circuit/main.py
'''

from src.Logging import init,logger
import logging
from src.plot import plotGUI
from PyQt5 import QtWidgets
import os
import sys


init()
logger.info('Main Function started')

os.chdir(os.path.dirname(os.path.abspath(__file__)))
root = os.getcwd()
path = root+'/Workspace/bin'
if path not in os.environ['PATH']:
    os.environ['PATH'] += ':'+path
del path

logger.debug(os.environ['PATH'])


app = QtWidgets.QApplication(sys.argv)
main = plotGUI(root)
main.show()
app.exec_()
logger.info(os.getcwd())
logger.info('Main Function stopped\n\n')