# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 30-06-2021 22:30:01
 LastEditors: Yichen Zhang
 LastEditTime: 05-07-2021 20:38:20
 FilePath: /circuit/src/_resultaly.py
'''
import logging
from timeit import default_timer as timer
import numpy as np
from scipy import stats
from scipy.special import erf
from scipy import interpolate


def resultdata(self, worst=False):
    start = timer()
    with open('fc', 'r') as fileobject, open('fc_wst', 'r') as wst, open('paramlist', 'r') as paramlist:
        fileobject.readline()
        lines = fileobject.readlines()
        param = paramlist.readlines()

        if worst:
            wst.readline()
            lines_wst = wst.readlines()

            self.wst_cutoff = np.zeros(len(lines_wst))
            i = 0
            for line in lines_wst:
                row = line.split()
                self.wst_cutoff[i] = float(line.split()[1])
                i += 1
            self.wst_cutoff.sort()

    self.cutoff = np.zeros(len(lines))
    i = 0
    for line in lines:
        self.cutoff[i] = float(line.split()[1])
        i += 1

    index = self.cutoff.argsort()
    self.cutoff = self.cutoff[index]
    cutoff0, index0 = np.unique(self.cutoff, return_index=True)
    length = len(self.cutoff)
    logging.info(f'Initial length={length}, Truncated length={len(cutoff0)}')

    for i in range(self.lengthc):
        self.alter_c[i].capacitance = np.append(
            self.alter_c[i].capacitance, np.zeros(self.mc_runs))
    for i in range(self.lengthr):
        self.alter_r[i].resistance = np.append(
            self.alter_r[i].resistance, np.zeros(self.mc_runs))

    i, j = 0, 0
    while i < len(param):
        for k in range(self.lengthc):
            self.alter_c[k].capacitance[j] = float(param[i].split()[-1])
            i += 1
        for k in range(self.lengthr):
            self.alter_r[k].resistance[j] = float(param[i].split()[-1])
            i += 1
        j += 1

    product = 1
    for i in range(self.lengthc):
        self.alter_c[i].fx = f(self.alter_c[i].capacitance, float(self.alter_c[i].c), float(
            self.alter_c[i].c)*self.alter_c[i].tol/3, self.alter_c[i].tol)*(float(self.alter_c[i].c)*self.alter_c[i].tol*2)
        product *= self.alter_c[i].fx
    for i in range(self.lengthr):
        self.alter_r[i].fx = f(self.alter_r[i].resistance, float(self.alter_r[i].r), float(
            self.alter_r[i].r)*self.alter_r[i].tol/3, self.alter_r[i].tol)*(float(self.alter_r[i].r)*self.alter_r[i].tol*2)
        product *= self.alter_r[i].fx

    seq = 0
    self.p = np.zeros(length)
    for i in range(length):
        seq += product[index[i]]
        self.p[i] = 1/length*seq

    # self.p = (self.p-self.p[0])/(self.p[-1]-self.p[0])  # Normalization
    for i in range(len(index0)-1):
        if index0[i+1]-index0[i] != 1:
            index0[i] = index0[i+1]-1
    if length-1-i != 1:
        index0[i+1] = length-1
    p0 = self.p[index0]
    self.fit = interpolate.PchipInterpolator(cutoff0, p0)
    logging.info(f'Analyse Data Time: {timer()-start}s')


def f(x, miu=2000, sigma=1, tol=0.01):
    return np.exp(-1/2*((x-miu)/sigma)**2)/(sigma*np.sqrt(2*np.pi)*(erf(tol*miu/sigma/np.sqrt(2))-erf(-tol*miu/sigma/np.sqrt(2)))/2)


def unif(miu=2000, tol=0.01):
    return stats.uniform(miu*(1-tol), 2*miu*tol)


def resultdata2(self, worst=False):
    with open('fc', 'r') as fileobject, open('fc_wst', 'r') as wst:
        fileobject.readline()
        lines = fileobject.readlines()

        if worst:
            wst.readline()
            lines_wst = wst.readlines()

            self.wst_cutoff = np.zeros(len(lines_wst))
            i = 0
            for line in lines_wst:
                row = line.split()
                self.wst_cutoff[i] = float(line.split()[1])
                i += 1
            self.wst_cutoff.sort()

    self.cutoff = np.zeros(len(lines))
    i = 0
    for line in lines:
        self.cutoff[i] = float(line.split()[1])
        i += 1

    self.cutoff.sort()
    length = len(self.cutoff)

    self.p = np.arange(1, 1+length)/length
