# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 30-06-2021 18:56:02
 LastEditors: Yichen Zhang
 LastEditTime: 06-07-2021 13:28:18
 FilePath: /circuit/src/is3.py
'''
import importlib
import sys
import logging.config
import logging
import os
import numpy as np
from scipy import interpolate
from matplotlib import pyplot as plt
import hashlib
import yaml
from timeit import default_timer as timer
isf = importlib.import_module('isf', 'src')
print(isf)


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
                # coloredlogs.install()
            except Exception as e:
                print(e)
                print('Error in Logging Configuration. Using default configs')
                logging.basicConfig(level=default_level)
                # coloredlogs.install(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        # coloredlogs.install(level=default_level)
        print('Failed to load configuration file. Using default configs')


def check_module(module_name):
    """
    Checks if module can be imported without actually
    importing it
    """
    module_spec = importlib.util.find_spec(module_name)
    if module_spec is None:
        print("Module: {} not found".format(module_name))
        raise ModuleNotFoundError("Module: {} not found".format(module_name))
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


def GetHashofDirs(directory, verbose=0):
    SHAhash = hashlib.md5()
    for item in directory:
        if not os.path.exists(item):
            return -1
        else:
            for root, dirs, files in os.walk(item):
                for names in files:
                    filepath = os.path.join(root, names)
                    if verbose == 1:
                        print('Hashing', filepath)
                    try:
                        f1 = open(filepath, 'rb')
                        SHAhash.update(f1.read())
                        f1.close()
                    except:
                        # You can't open the file for some reason
                        f1.close()
                        return

    return SHAhash.hexdigest()


if __name__=='__main__':

    spec=check_module('coloedlogs')


    isf.try2()

    logging.basicConfig(level=logging.DEBUG,format="%(asctime)s - %(filename)s - %(levelname)s - %(message)s")

    os.chdir('Workspace')
    if GetHashofDirs(['bin','share','include','lib/ngspice'])=='60687c6e167991cf8543dcbc521ebd47':
        os.makedirs('lib/user',exist_ok=True)
        logging.info('Initialization Successfully')
    else:
        logging.error('Initialization Failed')
        sys.exit('-1')

    print(__file__)
    print(os.path.abspath(__file__+'/../../'))

    '''
    print(isf.xyz)
    n=10000
    start=timer()
    x=np.random.randint(10000,size=n)
    y=np.random.rand(n)*n
    # print(x)
    x.sort()
    y.sort()
    # print(y)
    xx,index2=np.unique(x,return_index=True)
    print(len(x),len(xx))
    for i in range(len(index2)-1):
        if index2[i+1]-index2[i]!=1:
            index2[i]=index2[i+1]-1
    if len(x)-1-i!=1:
        index2[i+1]=len(x)-1
    yy=y[index2]
    fit=interpolate.PchipInterpolator(xx,yy)
    s=np.linspace(xx[0],xx[-1],10*n)
    print(timer()-start)
    plt.plot(s,fit(s),'b')
    plt.plot(x,y,'r')

    # plt.show()'''
