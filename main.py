# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 26-06-2021 14:43:04
 LastEditors: Yichen Zhang
 LastEditTime: 06-07-2021 00:30:43
 FilePath: /circuit/main.py
'''

from src import Logging
import logging
from src.plot import plotGUI
from PyQt5 import QtWidgets
import os
import sys


Logging.setup_logging('src/logging.yaml', logging.DEBUG)
Logging.init()
logging.info('Main Function started')

os.chdir(os.path.dirname(os.path.abspath(__file__)))
root = os.getcwd()
path = root+'/Workspace/bin'
if path not in os.environ['PATH']:
    os.environ['PATH'] += ':'+path
del path

logging.debug(os.environ['PATH'])


app = QtWidgets.QApplication(sys.argv)
main = plotGUI(root)
main.show()
app.exec_()
logging.info(os.getcwd())
logging.info('Main Function stopped\n\n')