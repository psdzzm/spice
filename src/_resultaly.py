# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 30-06-2021 22:30:01
 LastEditors: Yichen Zhang
 LastEditTime: 12-07-2021 16:37:58
 FilePath: /circuit/src/_resultaly.py
'''
import logging
import threading
from timeit import default_timer as timer
import numpy as np
from scipy import stats
from scipy.special import erf
from scipy import interpolate
import pandas as pd
import os,sys
from .Logging import check_module,import_module_from_spec
import threading


def resultdata(self, worst=False):
    start = timer()
    with open('fc', 'r') as fileobject, open('fc_wst', 'r') as wst, open('paramlist', 'r') as paramlist,open('paramwstlist','r') as paramwstlist:
        fileobject.readline()
        lines = fileobject.readlines()
        param = paramlist.readlines()
        paramwst=paramwstlist.readlines()

        if worst:
            wstframe=pd.DataFrame(columns=('','Left','Right'))
            wst.readline()
            lines_wst = wst.readlines()

            self.wst_cutoff = np.zeros(len(lines_wst))
            i = 0
            for line in lines_wst:
                row = line.split()
                self.wst_cutoff[i] = float(line.split()[1])
                i += 1

            self.stdcutoff=self.wst_cutoff[-1]
            self.wstindex=self.wst_cutoff.argsort()
            self.wst_cutoff=self.wst_cutoff[self.wstindex]
            wstframe.loc[0]=['Frequency',self.wst_cutoff[0],self.wst_cutoff[-1]]

            for i in range(self.lengthc):
                wstframe.loc[i+1]=[self.alter_c[i].name,float(paramwst[self.wstindex[0]*(self.lengthc+self.lengthr)+i].split()[-1]),float(paramwst[self.wstindex[-1]*(self.lengthc+self.lengthr)+i].split()[-1])]
            for i in range(self.lengthr):
                wstframe.loc[i+1+self.lengthc]=[self.alter_r[i].name,float(paramwst[self.wstindex[0]*(self.lengthc+self.lengthr)+i+self.lengthc].split()[-1]),float(paramwst[self.wstindex[-1]*(self.lengthc+self.lengthr)+i+self.lengthc].split()[-1])]

            self.wstframehtml='\n{% block wsttable %}\n'+wstframe.to_html(index=False,justify='center')+'\n{% endblock %}\n'

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
    self._fit = interpolate.PchipInterpolator(self.p0, self.cutoff0)
    self.fit = interpolate.PchipInterpolator(self.cutoff0, self.p0)
    logging.info(f'Analyse Data Time: {timer()-start}s')
    thread=threading.Thread(target=self.report,args=())
    thread.start()


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

    # cframe.set_table_styles([{'selector': 'th', 'props': [('font-size', '12pt')]}])
    # rframe.set_table_styles([{'selector': 'th', 'props': [('font-size', '12pt')]}])
    cframehtml='\n{% block ctable %}\n'+cframe.to_html(index=False)+'\n{% endblock %}\n'
    rframehtml='\n{% block rtable %}\n'+rframe.to_html(index=False)+'\n{% endblock %}\n'

    llimit=self.stdcutoff*(1-self.tol)
    rlimit=self.stdcutoff*(1+self.tol)
    if llimit<self.cutoff[0]:
        lfit=0
    else:
        lfit=self.fit(llimit)
    if rlimit>self.cutoff[-1]:
        rfit=0
    else:
        rfit=self.p[-1]-self.fit(rlimit)

    yd=1-rfit-lfit
    logging.info(f'Estimated yield: {yd}')

    rtail=pd.DataFrame(columns=('Frequency/Hz (Larger than)','Probability'))
    ltail=pd.DataFrame(columns=('Frequency/Hz (Smaller than)','Probability'))

    if yd>=self.yd:
        index1=np.linspace((1-self.yd)/2+0.05,(1-self.yd)/2,5,endpoint=False)
        index1=np.concatenate((index1,np.linspace((1-self.yd)/2,(1-yd)/2,5,endpoint=False)))

        index2=np.linspace(self.p0[-1]-(1-self.yd)/2-0.05,self.p0[-1]-(1-yd)/2,5,endpoint=False)
        index2=np.concatenate((index2,np.linspace(self.p0[-1]-(1-self.yd)/2,self.p0[-1]-(1-yd)/2,5,endpoint=False)))

        if (1-yd)/2 >0.0001:
            index1=np.concatenate((index1,np.linspace((1-yd)/2,0,5,endpoint=False)))
            index2=np.concatenate((index2,np.linspace(self.p0[-1]-(1-yd)/2,self.p0[-1],5,endpoint=False)))
    else:
        index1=np.linspace((1-yd)/2,(1-self.yd)/2,5,endpoint=False)
        index1=np.concatenate((index1,np.linspace((1-self.yd)/2,0,5,endpoint=False)))
        index2=np.linspace(self.p0[-1]-(1-yd)/2-0.05,self.p0[-1]-(1-self.yd)/2,5,endpoint=False)
        index2=np.concatenate((index2,np.linspace(self.p0[-1]-(1-self.yd)/2,self.p0[-1],5,endpoint=False)))

    for i in range(len(index1)):
        ltail.loc[i]=[self._fit(index1[i]),index1[i]]
        rtail.loc[i]=[self._fit(index2[i]),index1[i]]


    ltailhtml='\n{% block lefttail %}\n'+ltail.to_html(index=False)+'\n{% endblock %}\n'
    rtailhtml='\n{% block righttail %}\n'+rtail.to_html(index=False)+'\n{% endblock %}\n'


    from django.template.loader import render_to_string
    from django.template import Context, Template
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'report.settings')
    sys.path.append(os.path.dirname(__file__)+'/report')
    django.setup()

    with open(os.path.dirname(__file__)+'/report/htmlreport/templates/inherit.html','w+') as table,open(os.path.dirname(__file__)+'/report/htmlreport/templates/report.html','w') as rendered:
        table.write("{% extends 'base.html' %}\n"+cframehtml+rframehtml+ltailhtml+rtailhtml+self.wstframehtml)

        table.seek(0)

        files=table.read()

        t=Template(files)
        renddict={'title':self.shortname,'mc_runs':self.total,'port':self.netselect,'std':self.stdcutoff,'tol':self.tol,'yield':self.yd}

        if yd>=self.yd:
            renddict['comment']=f"This circuit design is acceptable. The estimated yield from simulation is {np.round(yd,6)}."
        else:
            renddict['comment']=f"This circuit design is not acceptable. The estimated yield from simulation is only {np.round(yd,4)}."

        if self.lengthc>1:
            renddict['cnumber']=f'{self.lengthc} Capacitors'
        else:
            renddict['cnumber']=f'{self.lengthc} Capacitor'

        if self.lengthr>1:
            renddict['rnumber']=f'{self.lengthr} Resistors'
        else:
            renddict['rnumber']=f'{self.lengthr} Resistor'

        context=Context(renddict)

        renderhtml=t.render(context)
        rendered.write(renderhtml)

        check=check_module('weasyprint')
        if check:
            wypt=import_module_from_spec(check)
            html=wypt.HTML(string=renderhtml)
            html.write_pdf('report.pdf')
            logging.info('Exporting report to '+self.dir)
        else:
            logging.warning("Can't findModule weasyprint! Fail to export pdf report. See html5 report in "+os.path.dirname(__file__)+'/report/htmlreport/templates/report.html')