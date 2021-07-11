# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 30-06-2021 22:30:01
 LastEditors: Yichen Zhang
 LastEditTime: 11-07-2021 19:12:18
 FilePath: /spice/src/_resultaly.py
'''
import logging
from timeit import default_timer as timer
import numpy as np
from scipy import stats
from scipy.special import erf
from scipy import interpolate
import pandas as pd
import os,sys


def resultdata(self, worst=False):
    start = timer()
    with open('fc', 'r') as fileobject, open('fc_wst', 'r') as wst, open('paramlist', 'r') as paramlist,open('paramwstlist','r') as paramwstlist:
        fileobject.readline()
        lines = fileobject.readlines()
        param = paramlist.readlines()
        paramwst=paramwstlist.readlines()

        if worst:
            wstdict={}
            wst.readline()
            lines_wst = wst.readlines()

            self.wst_cutoff = np.zeros(len(lines_wst))
            i = 0
            for line in lines_wst:
                row = line.split()
                self.wst_cutoff[i] = float(line.split()[1])
                i += 1
            self.wstindex=self.wst_cutoff.argsort()
            self.wst_cutoff=self.wst_cutoff[self.wstindex]

            for i in range(self.lengthc):
                wstdict[self.alter_c[i].name]=[float(paramwst[self.wstindex[0]*(self.lengthc+self.lengthr)+i].split()[-1]),float(paramwst[self.wstindex[-1]*(self.lengthc+self.lengthr)+i].split()[-1])]
            for i in range(self.lengthr):
                wstdict[self.alter_r[i].name]=[float(paramwst[self.wstindex[0]*(self.lengthc+self.lengthr)+i+self.lengthc].split()[-1]),float(paramwst[self.wstindex[-1]*(self.lengthc+self.lengthr)+i+self.lengthc].split()[-1])]

            print(self.wstindex[[0,-1]],wstdict)


    self.cutoff = np.zeros(len(lines))
    i = 0
    for line in lines:
        self.cutoff[i] = float(line.split()[1])
        i += 1

    index = self.cutoff.argsort()
    self.cutoff = self.cutoff[index]
    self.cutoff0, index0 = np.unique(self.cutoff, return_index=True)
    length = len(self.cutoff)
    logging.info(f'Initial length={length}, Truncated length={len(self.cutoff0)}')

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
    self.p0 = self.p[index0]
    self.fit = interpolate.PchipInterpolator(self.p0, self.cutoff0)
    logging.info(f'Analyse Data Time: {timer()-start}s')
    report(self)


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


def report(self):
    cframe=pd.DataFrame(columns=('Name','Value/F','Tolerance'))
    rframe=pd.DataFrame(columns=('Name','Value/Ω','Tolerance'))
    for i in range(self.lengthc):
        cframe.loc[i]=[self.alter_c[i].name,self.alter_c[i].c,self.alter_c[i].tol]
    for i in range(self.lengthr):
        rframe.loc[i]=[self.alter_r[i].name,self.alter_r[i].r,self.alter_r[i].tol]

    cframehtml='\n{% block ctable %}\n'+cframe.to_html(index=False)+'\n{% endblock %}\n'
    rframehtml='\n{% block rtable %}\n'+rframe.to_html(index=False)+'\n{% endblock %}\n'


    from django.template.loader import render_to_string
    from django.template import Context, Template
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'report.settings')
    sys.path.append(os.path.dirname(__file__)+'/report')
    django.setup()

    with open('/home/zyc/Desktop/projects/spice/src/report/htmlreport/templates/inherit.html','w+') as table,open('/home/zyc/Desktop/projects/spice/src/report/htmlreport/templates/report.html','w') as rendered:
        table.write("{% extends 'base.html' %}\n"+cframehtml+rframehtml)

        table.seek(0)

        t=Template(table.read())
        context=Context({'title':self.shortname,'cnumber':f'{self.lengthc} Capacitors','rnumber':f'{self.lengthr} Resistors'})

        rendered.write(t.render(context))

    tail=np.zeros(10)
    j=0
    p=np.concatenate((np.arange(0.01,0.06,0.01),np.arange(self.p0[-1]-0.05,self.p0[-1],0.01)))
    if len(p)>10:
        p=np.delete(p,10)

    for i in p:
        tail[j]=self.fit(i)
        j+=1

    np.savetxt('test.csv',np.column_stack((tail,np.concatenate((np.linspace(0.01,0.06,5,endpoint=False),np.linspace(0.95,1,5,endpoint=False))))),delimiter=',',fmt='%.4f')