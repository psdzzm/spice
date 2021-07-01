# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 01-07-2021 14:38:14
 LastEditors: Yichen Zhang
 LastEditTime: 01-07-2021 14:39:01
 FilePath: /circuit/Workspace/test/runspice.py
'''
from timeit import default_timer as timer
import os
import sys
from datetime import datetime
import getopt
import numpy as np


def rm(filename):
    try:
        os.remove(filename)
    except OSError:
        pass


def runspice(mode=0):
    start = timer()
    if mode:
        rm('fc_wst')
        os.system('ngspice -b run_control_wst.sp -o run_log')
    else:
        rm('fc2')
        os.system('ngspice -b run_control.sp -o run_log')


if __name__ == "__main__":
    n = 10
    time=np.zeros(n)
    for i in range(n):
        start=timer()
        runspice(0)
        time[i]=timer()-start
    print(time,np.mean(time))


