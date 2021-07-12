# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 26-06-2021 14:43:04
 LastEditors: Yichen Zhang
 LastEditTime: 12-07-2021 11:30:50
 FilePath: /circuit/main.py
'''

from src import Logging
import logging
from src import read_copy as read
from src.batch import batchmode
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

filename=read.getfile(root)
batch=batchmode(filename,root)
batch.openfile(filename)
batch.config()
batch.finish('Open')
batch.Cir.plotcdf()
'''
app = QtWidgets.QApplication(sys.argv)
main = plotGUI(root)
main.show()
app.exec_()
logging.info(os.getcwd())
logging.info('Main Function stopped\n\n')'''