# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 03-07-2021 18:53:46
 LastEditors: Yichen Zhang
 LastEditTime: 03-07-2021 19:09:54
 FilePath: /circuit/src/Logging.py
'''
import logging.config
import logging
import yaml
import os,sys
import importlib

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
            except Exception as e:
                print(e)
                print('Error in Logging Configuration. Using default configs')
                logging.basicConfig(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        print('Failed to load configuration file. Using default configs')

    check=check_module('coloedlogs')
    if check:
        coloredlogs=import_module_from_spec(check)
        coloredlogs.install(level=default_level,milliseconds=True,fmt='%(asctime)s - %(filename)s - %(levelname)s - %(message)s')

def check_module(module_name):
    """
    Checks if module can be imported without actually
    importing it
    """
    module_spec = importlib.util.find_spec(module_name)
    if module_spec is None:
        if module_name!='coloredlogs':
            sys.exit("ModuleNotFoundError: No module named {}".format(module_name))
    else:
        print("Module: {} can be imported".format(module_name))
        return module_spec

def import_module_from_spec(module_spec):
    """
    Import the module via the passed in module specification
    Returns the newly imported module
    """
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module

modulelist=['numpy','scipy','PyQt5','matplotlib']
for item in modulelist:
    check_module(item)