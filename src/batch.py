# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 10-07-2021 10:22:36
 LastEditors: Yichen Zhang
 LastEditTime: 12-07-2021 11:24:05
 FilePath: /circuit/src/batch.py
'''
import shutil
from datetime import datetime
import os,sys
import logging
import subprocess
from src import read_copy as read
import readline


def rlinput(prompt, prefill=''):
   readline.set_startup_hook(lambda: readline.insert_text(prefill))
   try:
      return input(prompt)  # or raw_input in Python 2
   finally:
      readline.set_startup_hook()



class batchmode():
    def __init__(self,filename,root):
        self.filename=filename
        self.root=root


    def openfile(self,filename):
        name = os.path.basename(filename)
        if os.path.abspath(filename+'/../../') != self.root+'/Workspace':
            dir = name.split('.')[0]+' ' + \
                datetime.now().strftime("%d%m%Y_%H%M%S")
            os.mkdir(self.root+'/Workspace/'+dir)
            os.chdir(self.root+'/Workspace/'+dir)
            shutil.copyfile(filename, os.getcwd()+f'/{name}')
            logging.info('Copy '+filename+' to '+os.getcwd()+f'/{name}')
        else:
            os.chdir(os.path.dirname(filename))
            files = os.listdir()
            files.remove(name)
            for item in files:
                os.remove(item)

        self.Cir=read.circuit(filename)
        self.Cir.shortname = name
        self.Cir.dir = os.getcwd()

        message = self.Cir.read()

        if message:
            sys.exit(message)
        else:
            message,flag=self.Cir.init()

        i = -1
        includefile = []
        while True:
            i += 1
            if flag:
                if i < self.Cir.includetime:
                    # print(message)
                    temp=read.getfile(self.root)
                    includefile.append(temp.split('/')[-1].split('.')[0])
                    if temp:
                        shutil.copyfile(temp, self.root+'/Workspace/lib/user/'+includefile[i])
                        logging.info('Copy '+temp+' to ' +self.root+'/Workspace/lib/user/'+includefile[i])
                        message, flag = self.Cir.fixinclude(includefile[i], flag)
                    else:
                        logging.warning('Exit. Deleting the uploaded include file')
                        for file in includefile:
                            read.rm('../lib/user/'+file)
                        return
                else:
                    logging.error(
                        'Incorrect include file provided! Reset the input circuit')
                    for file in includefile:
                        read.rm('../lib/user/'+file)
                    with open('test.cir', 'w') as f1, open('run.cir', 'w') as f2:
                        f1.write(self.Cir.testtext)
                        f2.write(self.Cir.runtext)
                    message, flag = self.Cir.init()
                    message = 'Please provide the correct file for the include file\n'+message
                    i = -1
                    includefile = []

            elif message:
                # print(message)
                for file in includefile:
                    read.rm('../lib/user/'+file)
                return

            else:
                break

        print('Finish')


    def config(self):
        print('out',self.Cir.net)

        self.Cir.netselect=rlinput('Please select which net to measure:',prefill='out')
        while True:
            if self.Cir.netselect in self.Cir.net or self.Cir.netselect=='out':
                break
            else:
                self.Cir.netselect=input('Please enter the correct net:')

        self.Cir.mc_runs=rlinput('Please enter how many times to run (>1):',prefill='1000')
        while True:
            if self.Cir.mc_runs.isnumeric() and int(self.Cir.mc_runs)>1:
                self.Cir.mc_runs=int(self.Cir.mc_runs)
                break
            else:
                self.Cir.mc_runs=input('Please enter a valid number (>1):')

        self.Cir.analmode = 0
        self.Cir.measmode = 'Cutoff Frequency'
        self.Cir.rfnum = 0
        self.Cir.risefall = 1

        message='Please enter the start frequency (Hz):'
        while True:
            try:
                self.Cir.startac=float(rlinput(message,prefill=self.Cir.startac))
            except ValueError:
                message='Please enter a valid number:'
            else:
                if self.Cir.startac>0:
                    break
                else:
                    message='Please enter a valid number:'

        message='Please enter the stop frequency (Hz):'
        while True:
            try:
                self.Cir.stopac=float(rlinput(message,prefill=self.Cir.stopac))
            except ValueError:
                message='Please enter a valid number:'
            else:
                if self.Cir.stopac>self.Cir.startac:
                    break
                else:
                    message='Stop frequency is lower than start frequenct! Please enter a valid number:'

        self.Cir.create_prerun()
        subprocess.run('ngspice -b run_control_pre.sp -o run_log',
                       shell=True, stdout=subprocess.DEVNULL)

        with open('run.log', 'a') as file_object, open('run_log') as b:
            file = b.read()
            file_object.write(file)
            read.rm('run_log')
            if 'out of interval' in file:
                logging.error('Cutoff frequency out of interval')
                sys.exit()

        self.Cir.create_sp()
        self.Cir.create_wst()
        self.start_process(1)


    def start_process(self,runmode=0):
        logging.info('Spice Started')
        if runmode == 0:
            p=subprocess.run('ngspice -b run_control.sp -o run_log',shell=True, stdout=sys.stdout)
        elif runmode == 1:
            read.rm('fc')
            read.rm('fc_wst')
            p=subprocess.run('ngspice -b run_control.sp run_control_wst.sp -o run_log',shell=True, stdout=sys.stdout)

        print('Finish')

    def finish(self,mode):
        with open('run.log', 'a') as file_object, open('run_log') as b:
            file = b.read()
            file_object.write(file)
            read.rm('run_log')
            if 'out of interval' in file:
                logging.error('Cutoff frequency out of interval')
                sys.exit('Cutoff frequency out of interval')
            elif mode == 'Add':
                self.Cir.total = self.Cir.total+self.Cir.mc_runs
                self.Cir.resultdata()
            elif mode == 'Open':
                self.Cir.total = self.Cir.mc_runs
                self.Cir.resultdata(worst=True)