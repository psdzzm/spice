# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 30-06-2021 18:56:02
 LastEditors: Yichen Zhang
 LastEditTime: 03-07-2021 01:23:42
 FilePath: /circuit/src/is3.py
'''
import logging.config
import logging
import os
import numpy as np
from scipy import interpolate
from matplotlib import pyplot as plt
import hashlib
import yaml
import coloredlogs
from timeit import default_timer as timer

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




if __name__=='__main__':
    # setup_logging('src/logging.yaml')

    # logging.debug("start func debug")

    # logging.info("exec func info")

    # logging.warning('warning')

    # logging.error("end func error")

    # logging.critical('Critical')

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

    plt.show()
    # xx=[10,3,5,7,9,2,3,5,7,11]

    # for i in range(10):
    #     # print(xx[index[0:i+1]])
    #     print(index[0:i+1])

    # a=np.array([2,3])
    # b=np.array([5,6])
    # c=a*b
    # print(c)

    # x=[]
    # x=np.append(x,[0,1,2,3])
    # print(x)