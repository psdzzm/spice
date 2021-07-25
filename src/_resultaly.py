# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 30-06-2021 22:30:01
 LastEditors: Yichen Zhang
 LastEditTime: 26-07-2021 00:22:13
 FilePath: /circuit/src/_resultaly.py
'''
from threading import Thread
from timeit import default_timer as timer
import numpy as np
from scipy import interpolate
from scipy.special import erf
import pandas as pd
import os
import sys
from .Logging import check_module, import_module, logger
from datetime import datetime

# Import weasyprint.HTML and bs4.BeautifulSoup if exist
wypt = import_module(check_module('weasyprint'), 'HTML')
btf = import_module(check_module('bs4'), 'BeautifulSoup')


'''
Analyse simulation data
'worst': If analysis worst case data
'add': If analysis only added result data
'mode': Analysis mode
'''


def resultdata(self, worst=False, add=False, mode=None):
    start = timer()

    if worst:   # Analyse worst case data
        with open('fc_wst', 'r') as wst, open('paramwstlist', 'r') as paramwstlist:
            wst.readline()  # Read variable name line
            lines_wst = wst.readlines()     # Read data
            paramwst = paramwstlist.readlines()
            wstframe = pd.DataFrame(columns=('', 'Left', 'Right'))  # Create dataframe to record the component value under worst case

            self.wst_cutoff = np.zeros(len(lines_wst))
            i = 0
            for line in lines_wst:
                row = line.split()
                self.wst_cutoff[i] = line.split()[1]
                i += 1

            self.stdcutoff = self.wst_cutoff[-1]        # Cutoff frequency of standard component value
            self.wstindex = self.wst_cutoff.argsort()   # Sort cutoff frequency using index sorting
            self.wst_cutoff = self.wst_cutoff[self.wstindex]    # Sort cutoff frequency
            wstframe.loc[0] = ['Frequency', self.wst_cutoff[0], self.wst_cutoff[-1]]    # Worst cutoff frequency

            # Find the component value of the worst case
            for i in range(self.lengthc):
                wstframe.loc[i + 1] = [self.alter_c[i].name, float(paramwst[self.wstindex[0] * (self.lengthc + self.lengthr) + i].split()[-1]), float(paramwst[self.wstindex[-1] * (self.lengthc + self.lengthr) + i].split()[-1])]
            for i in range(self.lengthr):
                wstframe.loc[i + 1 + self.lengthc] = [self.alter_r[i].name, float(paramwst[self.wstindex[0] * (self.lengthc + self.lengthr) + i + self.lengthc].split()[-1]), float(paramwst[self.wstindex[-1] * (self.lengthc + self.lengthr) + i + self.lengthc].split()[-1])]

            # Convert dataframe to html string
            self.wstframehtml = '\n{% block wsttable %}\n' + wstframe.to_html(index=False, justify='center') + '\n{% endblock %}\n'

    # Read results
    with open('fc', 'r') as fileobject:
        fileobject.readline()
        if add:     # If add mode, move the pointer to the last read time
            fileobject.seek(self._fctell)

        lines = fileobject.readlines()
        self._fctell = fileobject.tell()    # Record position of pointer

    cutoff = np.zeros(len(lines))
    i = 0
    if mode == 'Step':      # Step mode
        comp = np.zeros(len(lines))
        for line in lines:
            comp[i] = line.split()[0]   # Component value
            cutoff[i] = line.split()[1]  # Cutoff Frequency
            i += 1

        comp, index = np.unique(comp, return_index=True)    # Remove duplicate value and sort
        cutoff = cutoff[index]

        self.p = cutoff     # y axis
        self.cutoff = comp  # x axis
        self.fit = interpolate.PchipInterpolator(self.cutoff, self.p)   # Interpolate
        return

    else:
        with open('paramlist') as paramlist:   # Read raw altered component values
            if add:
                paramlist.seek(self._paramtell)

            param = paramlist.readlines()
            self._paramtell = paramlist.tell()

        for line in lines:
            # For numpy array, no need to use float() to convert first
            cutoff[i] = line.split()[1]
            i += 1

    if add:     # Add mode, append results to the data befpre
        self.cutoff = np.concatenate([self.cutoff, cutoff])
    else:
        self.cutoff = cutoff
    del cutoff

    index = self.cutoff.argsort()   # Use index sort method
    self.cutoff = self.cutoff[index]
    self.cutoff0, index0 = np.unique(self.cutoff, return_index=True)    # Remove duplicate value and sort
    length = len(self.cutoff)
    logger.info(f'Initial length={length}, Truncated length={len(self.cutoff0)}')

    # Analyse altered component value
    i, j = 0, 0
    alterc = np.zeros([self.lengthc, self.mc_runs])  # Capacitor, 2-D array
    alterr = np.zeros([self.lengthr, self.mc_runs])  # Resistor
    while i < len(param):
        # k: number of components
        # j: alter time
        for k in range(self.lengthc):
            alterc[k, j] = param[i].split()[-1]
            i += 1
        for k in range(self.lengthr):
            alterr[k, j] = param[i].split()[-1]
            i += 1
        j += 1

    # Concatenate results with original data
    if add:
        for i in range(self.lengthc):
            self.alter_c[i].capacitance = np.concatenate([self.alter_c[i].capacitance, alterc[i]])
        for i in range(self.lengthr):
            self.alter_r[i].resistance = np.concatenate([self.alter_r[i].resistance, alterr[i]])
    else:
        for i in range(self.lengthc):
            self.alter_c[i].capacitance = alterc[i]
        for i in range(self.lengthr):
            self.alter_r[i].resistance = alterr[i]

    del alterc, alterr
    logger.debug(f'Length:{len(self.alter_c[0].capacitance)}')

    # Apply importance sampling
    # Function 'f' refers to p(x)/q(x)
    product = 1
    for i in range(self.lengthc):
        # self.alter_c[i].fx
        product *= f(self.alter_c[i].capacitance, float(self.alter_c[i].c), float(self.alter_c[i].c) * self.alter_c[i].tol / 3, self.alter_c[i].tol) * (float(self.alter_c[i].c) * self.alter_c[i].tol * 2)
    for i in range(self.lengthr):
        # self.alter_r[i].fx
        product *= f(self.alter_r[i].resistance, float(self.alter_r[i].r), float(self.alter_r[i].r) * self.alter_r[i].tol / 3, self.alter_r[i].tol) * (float(self.alter_r[i].r) * self.alter_r[i].tol * 2)

    # Calculate probability in ascending order
    seq = 0
    self.p = np.zeros(length)
    for i in range(length):
        seq += product[index[i]]    # As result of altered component value is not in ascending order, call the result of index sorting to get the ascending order result
        self.p[i] = 1 / length * seq    # Get original probability

    # self.p = (self.p-self.p[0])/(self.p[-1]-self.p[0])  # Normalization

    # Below code is used to correct the probability of duplicate value
    for i in range(len(index0) - 1):
        if index0[i + 1] - index0[i] != 1:  # index0 is created from np.unique(), if the difference of adjcant value is not 1, this means duplicate occur
            index0[i] = index0[i + 1] - 1   # Get index of the occurance of last duplicate occur
    if length - 1 - i != 1:     # Duplicate of the last number
        index0[i + 1] = length - 1
    self.p0 = self.p[index0]    # Generate fixed probablity
    self._fit = interpolate.PchipInterpolator(self.p0, self.cutoff0)
    self.fit = interpolate.PchipInterpolator(self.cutoff0, self.p0)
    logger.info(f'Analyse Data Time: {timer()-start}s')

    # Create a new thread to generate report
    thread = Thread(target=self.report, args=())
    thread.start()


# Importance sampling, calculate p(x)/q(x)
def f(x, miu=2000, sigma=1, tol=0.01):
    return np.exp(-1 / 2 * ((x - miu) / sigma)**2) / (sigma * np.sqrt(2 * np.pi) * (erf(tol * miu / sigma / np.sqrt(2)) - erf(-tol * miu / sigma / np.sqrt(2))) / 2)


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

    self.p = np.arange(1, 1 + length) / length


# Create report
def report(self):
    cframe = pd.DataFrame(columns=('Name', 'Value/F', 'Tolerance'))
    rframe = pd.DataFrame(columns=('Name', 'Value/Ω', 'Tolerance'))
    for i in range(self.lengthc):
        cframe.loc[i] = [self.alter_c[i].name, self.alter_c[i].c, self.alter_c[i].tol]
    for i in range(self.lengthr):
        rframe.loc[i] = [self.alter_r[i].name, self.alter_r[i].r, self.alter_r[i].tol]

    cframehtml = '\n{% block ctable %}\n' + cframe.to_html(index=False) + '\n{% endblock %}\n'
    rframehtml = '\n{% block rtable %}\n' + rframe.to_html(index=False) + '\n{% endblock %}\n'

    llimit = self.stdcutoff * (1 - self.tol)
    rlimit = self.stdcutoff * (1 + self.tol)
    if llimit < self.cutoff[0]:
        lfit = 0
    else:
        lfit = self.fit(llimit)
    if rlimit > self.cutoff[-1]:
        rfit = 0
    else:
        rfit = self.p[-1] - self.fit(rlimit)

    yd = 1 - rfit - lfit
    logger.info(f'Estimated yield: {yd}')

    rtail = pd.DataFrame(columns=('Frequency/Hz (Larger than)', 'Probability'))
    ltail = pd.DataFrame(columns=('Frequency/Hz (Smaller than)', 'Probability'))

    if yd >= self.yd:
        index1 = np.linspace((1 - self.yd) / 2 + 0.05, (1 - self.yd) / 2, 5, endpoint=False)
        index1 = np.concatenate((index1, np.linspace((1 - self.yd) / 2, (1 - yd) / 2, 5, endpoint=False)))

        index2 = np.linspace(self.p0[-1] - (1 - self.yd) / 2 - 0.05, self.p0[-1] - (1 - yd) / 2, 5, endpoint=False)
        index2 = np.concatenate((index2, np.linspace(self.p0[-1] - (1 - self.yd) / 2, self.p0[-1] - (1 - yd) / 2, 5, endpoint=False)))

        if (1 - yd) / 2 > 0.0001:
            index1 = np.concatenate((index1, np.linspace((1 - yd) / 2, 0, 5, endpoint=False)))
            index2 = np.concatenate((index2, np.linspace(self.p0[-1] - (1 - yd) / 2, self.p0[-1], 5, endpoint=False)))
    else:
        index1 = np.linspace((1 - yd) / 2, (1 - self.yd) / 2, 5, endpoint=False)
        index1 = np.concatenate((index1, np.linspace((1 - self.yd) / 2, 0, 5, endpoint=False)))
        index2 = np.linspace(self.p0[-1] - (1 - yd) / 2 - 0.05, self.p0[-1] - (1 - self.yd) / 2, 5, endpoint=False)
        index2 = np.concatenate((index2, np.linspace(self.p0[-1] - (1 - self.yd) / 2, self.p0[-1], 5, endpoint=False)))

    for i in range(len(index1)):
        ltail.loc[i] = [self._fit(index1[i]), index1[i]]
        rtail.loc[i] = [self._fit(index2[i]), index1[i]]

    ltailhtml = '\n{% block lefttail %}\n' + ltail.to_html(index=False) + '\n{% endblock %}\n'
    rtailhtml = '\n{% block righttail %}\n' + rtail.to_html(index=False) + '\n{% endblock %}\n'

    from django.template import Context, Template
    from django import setup

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'report.settings')
    sys.path.append(os.path.dirname(__file__) + '/report')
    setup()

    with open(os.path.dirname(__file__) + '/report/htmlreport/templates/inherit.html', 'w+') as table, open(os.path.dirname(__file__) + '/report/htmlreport/templates/report.html', 'w') as rendered:
        table.write("{% extends 'base.html' %}\n" + cframehtml + rframehtml + ltailhtml + rtailhtml + self.wstframehtml)

        table.seek(0)

        t = Template(table.read())  # Html5 file to render

        renddict = {'title': self.basename, 'mc_runs': self.total, 'date': datetime.now().strftime("%d/%m/%Y %H:%M:%S UTC"), 'port': self.netselect, 'std': self.stdcutoff, 'tol': self.tol, 'yield': self.yd}

        if yd >= self.yd:
            renddict['comment'] = f"This circuit design is acceptable. The estimated yield from simulation is {np.round(yd,6)}."
        else:
            renddict['comment'] = f"This circuit design is not acceptable. The estimated yield from simulation is only {np.round(yd,4)}."

        if self.lengthc > 1:
            renddict['cnumber'] = f'{self.lengthc} Capacitors'
        else:
            renddict['cnumber'] = f'{self.lengthc} Capacitor'

        if self.lengthr > 1:
            renddict['rnumber'] = f'{self.lengthr} Resistors'
        else:
            renddict['rnumber'] = f'{self.lengthr} Resistor'

        context = Context(renddict)  # Context to render

        renderhtml = t.render(context)  # Render html
        if btf:  # If could, prettify the html string
            renderhtml = btf(renderhtml, 'html5lib').prettify()

        rendered.write(renderhtml)

        if wypt:    # If could ,convert to pdf
            html = wypt(string=renderhtml)
            html.write_pdf('report.pdf')
            logger.info('Exporting report to ' + self.dir)
        else:
            logger.warning("Can't findModule weasyprint! Fail to export pdf report. See html5 report in " + os.path.dirname(__file__) + '/report/htmlreport/templates/report.html')
