# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description: Initialize log file and doing some check
 Author: Yichen Zhang
 Date: 03-07-2021 18:53:46
 LastEditors: Yichen Zhang
 LastEditTime: 25-07-2021 22:49:51
 FilePath: /circuit/src/Logging.py
'''

import os
import logging.config
import logging
import hashlib
import yaml
import importlib
from shutil import copyfile


def check_module(module_name):
    """
    Checks if module can be imported without actually
    importing it
    """
    module_spec = importlib.util.find_spec(module_name)
    if module_spec is None:
        print("Module: {} does not exist".format(module_name))
    else:
        print("Module: {} can be imported".format(module_name))
        return module_name


def import_module(module_name, name=None):
    """
    Import the module via the passed in module specification
    Returns the newly imported module
    """
    if module_name == None:
        return
    else:
        module = importlib.import_module(module_name)

    if name == None:
        return module
    elif isinstance(name, str):
        print('Import ' + module_name + '.' + name)
        return getattr(module, name)
    elif isinstance(name, list):
        length = len(name)
        if length == 1:
            print('Import ' + module_name + '.' + name[0])
            return getattr(module, name[0])
        elif length > 1:
            sub = [None] * length
            for item, i in zip(name, range(length)):
                sub[i] = getattr(module, item)
                print('Import ' + module_name + '.' + item)
            return sub
        else:
            raise BaseException("Empty list")
    else:
        raise TypeError("Unsupported type {} of " + name)


modulelist = ['numpy', 'scipy', 'PyQt5', 'matplotlib', 'pandas', 'django', 'quantiphy']
for item in modulelist:
    if not check_module(item):
        raise ModuleNotFoundError("Module: {} not found".format(item))


# Get md5sum of directories
def GetHashofDirs(directory) -> str:
    SHAhash = hashlib.md5()
    for item in directory:
        if not os.path.exists(item):
            return -1
        else:
            filepath = []
            for root, _, files in os.walk(item):    # Iterate files in directory
                for names in files:
                    filepath.append(os.path.join(root, names))  # Return every file path in directory
            for subfile in sorted(filepath):
                try:
                    f1 = open(subfile, 'rb')
                    SHAhash.update(f1.read())   # Update md5sum
                    f1.close()
                except:
                    # You can't open the file for some reason
                    f1.close()
                    return -2

    return SHAhash.hexdigest()


# Setup logging file
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
                logging.config.dictConfig(config)   # Load logging settings from file logging.yaml
            except Exception as e:
                print(e)
                print('Error in Logging Configuration. Using default configs')
                logging.basicConfig(format='%(asctime)s - %(filename)s - %(levelname)s - %(message)s', level=logging.INFO)
    else:
        logging.basicConfig(format='%(asctime)s - %(filename)s - %(levelname)s - %(message)s', level=logging.INFO)
        print('Failed to load configuration file. Using default configs')

    logger = logging.getLogger('default')
    check = check_module('coloredlogs')
    if check:   # If has module coleredlogs
        coloredlogs = import_module(check)
        coloredlogs.install(level=default_level, milliseconds=True, logger=logger, fmt='%(asctime)s - %(filename)s - %(levelname)s - %(message)s')

    return logger


# Initialize
def init():
    # Check md5sum of ngspice folders
    if GetHashofDirs(['Workspace/bin', 'Workspace/share', 'Workspace/include', 'Workspace/lib/ngspice']) == '5691f9bebed5eee48e85997573b89f83':
        os.makedirs('Workspace/lib/user', exist_ok=True)  # Make directory that contains include files uploaded by users
        home = os.path.expanduser('~') + '/.spiceinit'
        if (not os.path.isfile(home)) or (hashlib.md5(open(home, 'rb').read()).hexdigest() != '2dff7b8b4b76866c7114bb9a866ab600'):  # Check if file .spiceinit exists
            logger.info("Create '.spiceinit' file")
            copyfile('Workspace/.spiceinit', home)
        logger.info('Initialization Successfully')
    else:
        logger.error('Initialization Failed')
        raise


logger = setup_logging('src/logging.yaml', logging.DEBUG)
