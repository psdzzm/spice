# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 26-06-2021 14:43:04
 LastEditors: Yichen Zhang
 LastEditTime: 03-07-2021 13:06:02
 FilePath: /circuit/main.py
'''

from src.plot import plotGUI
from PyQt5 import QtWidgets
import os,sys
import logging.config
import logging
import yaml
import coloredlogs

def setup_logging(default_path='logging.yaml', default_level=logging.INFO, env_key='LOG_CFG'):
    """
    | **@author:** Prathyush SP
    | Logging Setup
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
                coloredlogs.install(level=default_level,milliseconds=True,fmt='%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
            except Exception as e:
                print(e)
                print('Error in Logging Configuration. Using default configs')
                logging.basicConfig(level=default_level)
                coloredlogs.install(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        coloredlogs.install(level=default_level)
        print('Failed to load configuration file. Using default configs')


setup_logging('src/logging.yaml',logging.DEBUG)
logging.info('Main Function started')

os.chdir(os.path.dirname(os.path.abspath(__file__)))
root=os.getcwd()
path=root+'/Workspace/bin'
if path not in os.environ['PATH']:
    os.environ['PATH']+=':'+path
del path

logging.debug(os.environ['PATH'])


app = QtWidgets.QApplication(sys.argv)
main = plotGUI(root)
main.show()
app.exec_()
logging.info(os.getcwd())
logging.info('Main Function stopped\n\n')