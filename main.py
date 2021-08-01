# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 26-06-2021 14:43:04
 LastEditors: Yichen Zhang
 LastEditTime: 01-08-2021 15:11:15
 FilePath: /spice/main.py
'''

from src.Logging import init, logger
from src.plot import plotGUI
from PyQt5.QtWidgets import QApplication
import os
import sys


init()
logger.info('Main Function started')

root = os.path.dirname(os.path.abspath(__file__))   # Root directory of main function
os.chdir(root)
path = os.path.join(root, 'Workspace', 'bin')
if path not in os.environ['PATH']:  # Add ngspice path to environ
    os.environ['PATH'] = path + ':' + os.environ['PATH']
del path

logger.debug(os.environ['PATH'])


app = QApplication(sys.argv)
main = plotGUI(root)
main.show()
app.exec_()
logger.info(os.getcwd())
logger.info('Main Function stopped\n\n')
