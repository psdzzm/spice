# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 03-07-2021 18:53:46
 LastEditors: Yichen Zhang
 LastEditTime: 12-07-2021 01:55:10
 FilePath: /circuit/src/Logging.py
'''

import importlib

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
        return module_spec


def import_module_from_spec(module_spec):
    """
    Import the module via the passed in module specification
    Returns the newly imported module
    """
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


modulelist = ['numpy', 'scipy', 'PyQt5','matplotlib', 'yaml', 'logging', 'hashlib','subprocess','shutil','datetime','timeit']
for item in modulelist:
    check=check_module(item)
    if not check:
        raise ModuleNotFoundError("Module: {} not found".format(item))

import yaml
import hashlib
import logging
import logging.config
import os

def GetHashofDirs(directory):
    SHAhash = hashlib.md5()
    for item in directory:
        if not os.path.exists(item):
            return -1
        else:
            filepath = []
            for root, _, files in os.walk(item):
                for names in files:
                    filepath.append(os.path.join(root, names))
            for subfile in sorted(filepath):
                try:
                    f1 = open(subfile, 'rb')
                    SHAhash.update(f1.read())
                    f1.close()
                    # print(subfile,SHAhash.hexdigest())
                except:
                    # You can't open the file for some reason
                    f1.close()
                    return

    return SHAhash.hexdigest()


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

    check = check_module('coloredlogs')
    if check:
        coloredlogs = import_module_from_spec(check)
        coloredlogs.install(level=default_level, milliseconds=True,
                            fmt='%(asctime)s - %(filename)s - %(levelname)s - %(message)s')


def init():
    if GetHashofDirs(['Workspace/bin', 'Workspace/share', 'Workspace/include', 'Workspace/lib/ngspice']) == '5691f9bebed5eee48e85997573b89f83':
        os.makedirs('lib/user', exist_ok=True)
        home = os.path.expanduser('~')+'/.spiceinit'
        if (not os.path.isfile(home)) or (hashlib.md5(open(home, 'rb').read()).hexdigest() != '2dff7b8b4b76866c7114bb9a866ab600'):
            logging.info("Create '.spiceinit' file")
            with open(home, 'w') as f:
                f.write('* User defined ngspice init file\n\n\tset filetype=ascii\n\tset color0=white\n\t*set wr_vecnames\t\t$ wrdata: scale and data vector names are printed on the first row\n\tset wr_singlescale\t$ the scale vector will be printed only once\n\n* unif: uniform distribution, deviation relativ to nominal value\n* aunif: uniform distribution, deviation absolut\n* gauss: Gaussian distribution, deviation relativ to nominal value\n* agauss: Gaussian distribution, deviation absolut\n* limit: if unif. distributed value >=0 then add +avar to nom, else -avar\n\n\tdefine unif(nom, rvar) (nom + (nom*rvar) * sunif(0))\n\tdefine aunif(nom, avar) (nom + avar * sunif(0))\n\tdefine gauss(nom, rvar, sig) (nom + (nom*rvar)/sig * sgauss(0))\n\tdefine agauss(nom, avar, sig) (nom + avar/sig * sgauss(0))\n\tdefine limit(nom, avar) (nom + ((sgauss(0) >= 0) ? avar : -avar))\n')
        logging.info('Initialization Successfully')
    else:
        logging.error('Initialization Failed')
        raise


# setup_logging('src/logging.yaml', logging.INFO)