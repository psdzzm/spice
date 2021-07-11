# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description: Read Circuit File
 Author: Yichen Zhang
 Date: 26-06-2021 14:43:04
 LastEditors: Yichen Zhang
 LastEditTime: 10-07-2021 16:24:35
 FilePath: /spice/src/read.py
'''


import logging
import os
import shutil
import subprocess
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
        self.resistance = []    # Alter paramater list


class C:
    def __init__(self, name, c, tol=0.05):
        self.name = name
        self.c = c
        self.tol = tol
        self.capacitance = []


class circuit:
    def __init__(self, filename):
        self.name = filename
        self.seed = int(time.time())
        self.mc_runs = 1000
        self.tolc = 0.05
        self.tolr = 0.01

        self.libpath = os.path.abspath(os.getcwd()+'/../lib')+'/'

    def read(self):
        fileo, files = [], []
        start, stop1, stop2, self.includetime = 0, 0, 0, 0
        matches = ['.model', '.subckt', '.global', '.include', '.lib',
                   '.param', '.func', '.temp', '.control', '.endc', '.end', '.ends']
        with open(self.name) as file_object:
            i = -1
            for lines in file_object:
                i += 1
                row = lines.split()
                if row == []:
                    continue
                elif not start:
                    if row[0].lower() == '.control':
                        start = i
                        continue
                elif not stop1:
                    if row[0].lower() == '.endc':
                        stop1 = i
                    continue

                if row[0].lower() == '.end':
                    stop2 = i
                    break
                # Filter other control command
                elif row[0].lower() not in matches and '.' in row[0].lower():
                    continue
                elif row[0].lower() == '.include':
                    self.includetime += 1
                    inclname = os.path.basename(row[1]).split('.')[0].upper()
                    path2check = self.libpath+'user/'+inclname  # Only file name without extension
                    # Directory lib has include file
                    if os.path.isfile(self.libpath+inclname):
                        lines = '.include ../lib/'+inclname+'\n'
                    # Source Directory has
                    elif os.path.isfile(os.path.dirname(self.name)+'/'+row[1]):
                        lines = '.include ../lib/user/'+inclname+'\n'
                        shutil.copyfile(os.path.dirname(
                            self.name)+'/'+row[1], path2check)
                        logging.info('Copy '+row[1]+' to '+path2check)
                    else:           # Directory ../lib/user has include file or will be later copied to
                        lines = '.include ../lib/user/'+inclname+'\n'

                fileo.append(lines)
                files.append(row)


        if stop1-start < 0:
            logging.error("No 'endc' line!")
            return "No 'endc' line!"
        elif not stop2:
            logging.error("No 'end' line!")
            return "No 'end' line!"
        else:
            fileo = ''.join(fileo)+'\n.end'

        with open('test.cir', 'w+') as file_object, open('run.cir', 'w+') as b, open('test_control.sp', 'w') as tsc:
            file_object.write(fileo)
            b.write(fileo)
            file_object.seek(0)
            self.testtext = file_object.read()
            b.seek(0)
            self.runtext = b.read()

            tsc.write(
                '*ng_script\n\n.control\n\tset wr_vecnames\n\tsource test.cir\n\tshow r : resistance , c : capacitance > list\n\top\n\twrdata op all\n.endc\n\n.end')

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
            file_object.truncate()
            file_object.write(test)

            b.seek(0)
            b.truncate()
            b.write(run)

        return self.init()

    def init(self):
        rm('run.log')
        logging.info('Checking if the input circuit is valid.')
        proc = subprocess.Popen(
            'ngspice -b test_control.sp -o test.log', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        _, stderr = proc.communicate()
        if stderr:
            logging.error(stderr.decode(
                'ASCII')+'Please check if the netlist file or include file is valid')
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
                        logging.error(''.join(error_r))
                        return ''.join(error_r), flag

                    error_r.append(fileo[i])
                    i += 1
                    while fileo[i].startswith('  '):
                        error_r.append(fileo[i])
                        i += 1
                else:
                    i += 1

            if error_r:
                logging.error(''.join(error_r))
                return ''.join(error_r), flag
            else:
                try:
                    self.net.remove('out')
                    self.netc.remove('out')
                    self.net.sort()
                    self.netc.sort()
                except ValueError:
                    logging.error("Error! No 'out' port!")
                    return "Error! No 'out' port!", flag

        with open('test_control2.sp', 'w') as file_object:
            file_object.write(
                f"*ng_script\n\n.control\n\tset wr_vecnames\n\tsource test.cir\n\tsave out {' '.join(self.net)}\n\tac dec 40 1 1G\n\twrdata ac all\n.endc\n\n.end ")

        subprocess.run('ngspice test_control2.sp -b -o test2.log',
                       shell=True, stdout=subprocess.DEVNULL)

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
        logging.info('Check successfully! Running simulation.')

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

    from ._write import create_prerun, create_sp, create_wst, create_sp2

    from ._resultaly import resultdata, resultdata2

    def plotcdf(self):
        plt.title("Cdf of Cutoff Frequency")
        plt.xlabel("Cutoff Frequency/Hz")
        plt.ylabel("Cdf")
        plt.grid()
        plt.plot(self.cutoff, self.p)
        plt.show()
