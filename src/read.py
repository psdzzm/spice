# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description: Read Circuit File
 Author: Yichen Zhang
 Date: 26-06-2021 14:43:04
 LastEditors: Yichen Zhang
 LastEditTime: 01-07-2021 00:02:50
 FilePath: /circuit/src/read.py
'''


import os
import shutil
import subprocess
import hashlib
import time
import re
import numpy as np
from matplotlib import pyplot as plt
import operator
from .runspice import runspice


def rm(filename):
    try:
        os.remove(filename)
    except OSError:
        pass


def getfile():
    filename = input('Please enter the filename: ')
    while True:
        if os.path.isfile(filename):
            return filename
        else:
            filename = input(
                f'{filename} does no exist! Please enter the correct filename: ')


class R:
    def __init__(self, name, r, tol=0.01):
        self.name = name
        self.r = r
        self.tol = tol
        self.resistance=[]


class C:
    def __init__(self, name, c, tol=0.05):
        self.name = name
        self.c = c
        self.tol = tol
        self.capacitance=[]


class circuit:
    def __init__(self, filename):
        self.name = filename
        self.seed = int(time.time())
        self.mc_runs = 1000
        self.tolc = 0.05
        self.tolr = 0.01

        self.libpath = os.getcwd()+'/../lib/'
        print(os.getcwd())

    def read(self):
        fileo, files = [], []
        start, stop1, stop2 = 0, 0, 0
        matches = ['.model', '.subckt', '.global', '.include', '.lib',
                   '.param', '.func', '.temp', '.control', '.endc', '.end', '.ends']
        with open(self.name) as file_object:
            for lines in file_object:
                row = lines.split()
                if row != [] and row[0].lower() not in matches and '.' in row[0].lower():
                    continue
                elif row != [] and row[0].lower() == '.include':
                    inclname = row[1].split('/')[-1].split('.')[0].upper()
                    path2check = self.libpath+'user/'+inclname  # Only file name without extension
                    # Directory lib has include file
                    if os.path.isfile(self.libpath+inclname):
                        lines = '.include ../lib/'+inclname+'\n'
                    # Source Directory has
                    elif os.path.isfile(os.path.dirname(self.name)+'/'+row[1]):
                        lines = '.include ../lib/user/'+inclname+'\n'
                        shutil.copyfile(os.path.dirname(
                            self.name)+'/'+row[1], path2check)
                        print('Copy '+row[1]+' to '+path2check)
                    else:           # Directory ../lib/user has include file or will be later copied to
                        lines = '.include ../lib/user/'+inclname+'\n'

                fileo.append(lines)
                files.append(row)

        length = len(files)
        for i in range(length):
            if files[i] != []:
                if files[i][0].lower() == '.control':
                    start = i
                elif files[i][0].lower() == '.endc':
                    stop1 = i
                elif files[i][0].lower() == '.end':
                    stop2 = i
                    break

        if not stop2:
            return "No 'end' line!"

        with open('test.cir', 'w') as file_object, open('run.cir', 'w') as b, open('test_control.sp', 'w') as tsc:
            if start and stop1:
                file_object.write(''.join(fileo[0:start]))
                file_object.write(''.join(fileo[stop1+1:stop2+1]))

                b.write(''.join(fileo[0:start]))
                b.write(''.join(fileo[stop1+1:stop2+1]))

            else:
                file_object.write(''.join(fileo[0:stop2]))
                file_object.write('\n.end')

                b.write(''.join(fileo[0:stop2]))
                b.write('.end')

            tsc.write(
                '*ng_script\n\n.control\n\tsource test.cir\n\tshow r : resistance , c : capacitance > list\n\top\n\twrdata op all\n.endc\n\n.end')

    def fixinclude(self, repl, mode):
        with open('test.cir', 'r+') as file_object, open('run.cir', 'r+') as b:
            test = file_object.read()
            run = b.read()
            if mode == 1:     # Include error
                test = test.replace('.include ../lib/user/'+self.subckt,
                                    '.include ../lib/user/'+repl)
                run = run.replace('.include ../lib/user/'+self.subckt,
                                  '.include ../lib/user/'+repl)
            elif mode == 2:   # Subcircuit error
                test = test.replace(
                    '.control\n', '.include ../lib/user/'+repl+'\n.control\n')
                run = run[:-4]+'.include ../lib/user/'+repl+'\n.end'

            file_object.seek(0)
            file_object.write(test)

            b.seek(0)
            b.write(run)

        return self.init()

    def init(self):
        rm('run.log')
        print('\nChecking if the input circuit is valid.\n')
        home = os.path.expanduser('~')
        if (not os.path.isfile(home+'/.spiceinit')) or (hashlib.md5(open(home+'/.spiceinit', 'rb').read()).hexdigest() != '57cc72ae38d0f359a525a1d32e638140'):
            with open(home+'/.spiceinit', 'w') as f:
                f.write('* User defined ngspice init file\n\n    set filetype=ascii\n\tset color0=white\n\tset wr_vecnames\t\t$ wrdata: scale and data vector names are printed on the first row\n\tset wr_singlescale\t$ the scale vector will be printed only once\n\n* unif: uniform distribution, deviation relativ to nominal value\n* aunif: uniform distribution, deviation absolut\n* gauss: Gaussian distribution, deviation relativ to nominal value\n* agauss: Gaussian distribution, deviation absolut\n* limit: if unif. distributed value >=0 then add +avar to nom, else -avar\n\n\tdefine unif(nom, rvar) (nom + (nom*rvar) * sunif(0))\n\tdefine aunif(nom, avar) (nom + avar * sunif(0))\n\tdefine gauss(nom, rvar, sig) (nom + (nom*rvar)/sig * sgauss(0))\n\tdefine agauss(nom, avar, sig) (nom + avar/sig * sgauss(0))\n\tdefine limit(nom, avar) (nom + ((sgauss(0) >= 0) ? avar : -avar))\n')
        proc = subprocess.Popen(
            'ngspice -b test_control.sp -o test.log', shell=True, stderr=subprocess.PIPE)
        _, stderr = proc.communicate()
        if stderr:
            return stderr.decode('ASCII')+'Please check if the netlist file or include file is valid', False

        self.readnet()

        with open('test.log') as file_object:
            fileo = file_object.readlines()
            error_r = []
            i = 0
            flag = 0
            while i < len(fileo):
                if fileo[i].lower().startswith('error'):
                    # elif fileo[i] == 'Error: measure  cut  (WHEN) : out of interval\n':
                    #     return "Error! No AC stimulus found or cutoff frequency out of range:\nSet the value of a current or voltage source to 'AC 1.'to make it behave as a signal generator for AC analysis.", flag
                    if 'Could not find include file' in fileo[i]:
                        self.subckt = fileo[i].split(
                        )[-1].replace('../lib/user/', '').rstrip()
                        fileo[i] = fileo[i].replace('../lib/user/', '') + \
                            f"Please provide the simulation model file for {self.subckt}\n"
                        flag = 1    # Include Error
                    elif 'unknown subckt' in fileo[i]:
                        self.subckt = fileo[i].split(
                        )[-1].replace('../lib/user/', '').rstrip().upper()
                        fileo[i] = fileo[i].replace('../lib/user/', '') + \
                            f"Please provide the simulation model file for {self.subckt}\n"
                        flag = 2    # Subcircuit Error
                    elif 'fatal error' in fileo[i]:
                        error_r.append(fileo[i])
                        return ''.join(error_r), flag

                    error_r.append(fileo[i])
                    i += 1
                    while fileo[i].startswith('  '):
                        error_r.append(fileo[i])
                        i += 1
                else:
                    i += 1

            if error_r:
                return ''.join(error_r), flag
            else:
                try:
                    self.net.remove('out')
                    self.netc.remove('out')
                    self.net.sort()
                    self.netc.sort()
                except ValueError:
                    return "Error! No 'out' port!", flag

        with open('test_control2.sp', 'w') as file_object:
            file_object.write(
                f"*ng_script\n\n.control\n\tsource test.cir\n\tsave out {' '.join(self.net)}\n\tac dec 40 1 1G\n\twrdata ac all\n.endc\n\n.end ")

        os.system('ngspice test_control2.sp -b -o test2.log')

        with open('ac') as file_object:
            title = file_object.readline().split()
            data = file_object.readlines()
            self.initx = np.zeros(len(data))
            length = len(self.net)+1
            self.inity = np.zeros([length, len(data)], dtype=np.complex_)

            index = [i for i, x in enumerate(title) if x == "out"]
            i = 0
            if len(index) == 1:
                for item in self.netc:
                    index.append(title.index(item))
                for line in data:
                    line = line.split()
                    self.initx[i] = float(line[0])
                    for j in range(length):
                        self.inity[j, i] = float(line[index[j]])
                    i += 1
            else:
                index = [index]
                for item in self.netc:
                    index.append([i for i, x in enumerate(title) if x == item])
                for line in data:
                    line = line.split()
                    self.initx[i] = float(line[0])
                    for j in range(length):
                        self.inity[j, i] = float(
                            line[index[j][0]])+float(line[index[j][1]])*1j
                    i += 1

            self.inity = 20*np.log10(np.abs(self.inity))

        with open('list') as file_object:
            self.alter_r = []
            self.alter_c = []
            files = []
            for lines in file_object:
                files.append(lines.split())

            length = len(files)
            for i in range(length):
                if files[i][0] == 'device':
                    for j in range(1, len(files[i])):
                        if 'r.x' not in files[i][j] and 'c.x' not in files[i][j]:
                            if files[i+2][0] == 'resistance':
                                self.alter_r.append(
                                    R(files[i][j], files[i+2][j]))
                            elif files[i+2][0] == 'capacitance':
                                self.alter_c.append(
                                    C(files[i][j], files[i+2][j]))

        self.lengthc = len(self.alter_c)
        self.lengthr = len(self.alter_r)
        self.alter_c.sort(key=operator.attrgetter('name'))
        self.alter_r.sort(key=operator.attrgetter('name'))
        print('Check successfully! Running simulation.\n')

        return flag, flag

    def readnet(self):
        with open('op') as file_object:
            nets = list(set(file_object.readline().split()))
            self.net = []
            self.netc = []
            for item in nets:
                if '#branch' in item:
                    continue
                else:
                    temp = re.match(r'x[\d\w]+\.', item)
                    if not temp:
                        m = re.match(r'V\((\d+)\)', item)
                        if m:
                            self.netc.append(m.group())
                            self.net.append(m.group(1))
                        else:
                            self.netc.append(item)
                            self.net.append(item)

    from ._write import create_sp, create_wst

    def ngspice(self, mode=0):
        runspice(mode)

    _col2 = []
    wst_cutoff = []

    from ._resultaly import resultdata

    def resultdata2(self, appnd=False, worst=True):
        with open('fc', 'r') as fileobject, open('fc_wst', 'r') as wst:
            fileobject.readline()
            lines = fileobject.readlines()

            if worst:
                wst.readline()
                lines_wst = wst.readlines()

                wstdata = []
                for line in lines_wst:
                    row = line.split()
                    wstdata.append(row[1])

                self.wst_cutoff = np.zeros(len(wstdata))
                for i in range(len(wstdata)):
                    self.wst_cutoff[i] = float(wstdata[i])

        if not appnd:
            self._col2 = []

        for line in lines:
            row = line.split()
            self._col2.append(row[1])

        length = len(self._col2)
        self.cutoff = np.zeros(length)

        for i in range(length):
            self.cutoff[i] = float(self._col2[i])

        if worst:
            self.cutoff = np.append(self.cutoff, self.wst_cutoff)

        self.cutoff = np.sort(np.array(list(set(self.cutoff))))
        self.wst_index = np.where(np.isin(self.cutoff, self.wst_cutoff))
        length = len(self.cutoff)

        xaxis = np.linspace(self.cutoff[0], self.cutoff[-1], length)
        self.p = np.arange(1, 1+length)/length

    def plotcdf(self):
        plt.title("Cdf of Cutoff Frequency")
        plt.xlabel("Cutoff Frequency/Hz")
        plt.ylabel("Cdf")
        plt.grid()
        plt.plot(self.cutoff, self.p)
        plt.show()
