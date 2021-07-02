# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 26-06-2021 14:43:04
 LastEditors: Yichen Zhang
 LastEditTime: 02-07-2021 20:16:25
 FilePath: /circuit/src/_write.py
'''
import time


def create_prerun(self):
    if self.measmode == 'Cutoff Frequency':
        if self.risefall:
            self.rfmode = 'fall='
        else:
            self.rfmode = 'rise='
        if self.rfnum == 0:
            self.rfmode = self.rfmode+'last'
        else:
            self.rfmode = self.rfmode+str(self.rfnum)

    control = f"*ng_script\n\n.control\n\tsource run.cir\n\tsave {self.netselect}\n\tac dec 40 {self.startac} {self.stopac}\n\tmeas ac ymax MAX v({self.netselect})\n\tlet v3db = ymax/sqrt(2)\n\tmeas ac cut when v({self.netselect})=v3db {self.rfmode}\n\tprint cut > cutoff\n.endc\n\n.end"

    with open('run_control_pre.sp', 'w') as file_object:
        file_object.write(control)


def create_sp2(self,add=False):
    self.seed = int(time.time())

    if add:
        self.control = [
            f"*ng_script\n\n.control\n\tsource run.cir\n\tsave {self.netselect}\n\tset appendwrite\n\tlet mc_runs = {self.mc_runs}\n\tlet run = 0\n\tset curplot=new          $ create a new plot\n\tset scratch=$curplot     $ store its name to 'scratch'\n\tlet cutoff=unitvec(mc_runs)\n\tsetseed {self.seed}\n\n"]
    else:
        self.control = [
            f"*ng_script\n\n.control\n\tsource run.cir\n\tsave {self.netselect}\n\tset wr_vecnames appendwrite\n\tlet mc_runs = {self.mc_runs}\n\tlet run = 0\n\tset curplot=new          $ create a new plot\n\tset scratch=$curplot     $ store its name to 'scratch'\n\tlet cutoff=unitvec(mc_runs)\n\tsetseed {self.seed}\n\n"]
    loop = '\tdowhile run < mc_runs\n\t\t'

    for i in range(self.lengthc):
        loop = loop+'alter ' + \
            self.alter_c[i].name + \
            '=gauss('+self.alter_c[i].c + \
                    f',{self.alter_c[i].tol},3)\n\t\t'
    for i in range(self.lengthr):
        loop = loop+'alter ' + \
            self.alter_r[i].name + \
            '=gauss('+self.alter_r[i].r + \
                    f',{self.alter_r[i].tol},3)\n\t\t'

    if self.measmode == 'Cutoff Frequency':
        if self.risefall:
            self.rfmode = 'fall='
        else:
            self.rfmode = 'rise='
        if self.rfnum == 0:
            self.rfmode = self.rfmode+'last'
        else:
            self.rfmode = self.rfmode+str(self.rfnum)

        self.control.append(
            f'ac dec 40 {self.startac} {self.stopac}\n\n\t\tmeas ac ymax MAX v({self.netselect})\n\t\tlet v3db = ymax/sqrt(2)\n\t\tmeas ac cut when v({self.netselect})=v3db {self.rfmode}\n\t\tlet {{$scratch}}.cutoff[run] = cut\n\t\tdestroy $curplot\n\t\tlet run = run + 1\n\tend\n\n\tsetplot $scratch\n\t')

    else:
        self.control.append(
            f'ac dec 40 {self.startac} {self.stopac}\n\n\t\tmeas ac y{self.measmode} {self.measmode} v({self.netselect})\n\t\tlet {{$scratch}}.cutoff[run] = y{self.measmode}\n\t\tdestroy $curplot\n\t\tlet run = run + 1\n\tend\n\n\tsetplot $scratch\n\t')

    self.control.append('wrdata fc cutoff\n.endc\n\n.end')

    with open('run_control.sp', 'w') as file_object:
        file_object.write(self.control[0])
        file_object.write(loop)
        file_object.write(self.control[1])
        file_object.write(self.control[2])


def create_sp(self, add=False):
    self.seed = int(time.time())

    if add:
        self.control = [
            f"*ng_script\n\n.control\n\tsource run.cir\n\tsave {self.netselect}\n\tset appendwrite\n\tlet mc_runs = {self.mc_runs}\n\tlet run = 0\n\tset curplot=new          $ create a new plot\n\tset scratch=$curplot     $ store its name to 'scratch'\n\tlet cutoff=unitvec(mc_runs)\n\tsetseed {self.seed}\n\n"]
    else:
        self.control = [
            f"*ng_script\n\n.control\n\tsource run.cir\n\tsave {self.netselect}\n\tset wr_vecnames appendwrite\n\tlet mc_runs = {self.mc_runs}\n\tlet run = 0\n\tset curplot=new          $ create a new plot\n\tset scratch=$curplot     $ store its name to 'scratch'\n\tlet cutoff=unitvec(mc_runs)\n\tsetseed {self.seed}\n\n"]
    loop = '\tdowhile run < mc_runs\n\t\t'

    for i in range(self.lengthc):
        loop = loop+'alter ' + \
            self.alter_c[i].name + \
            '=unif('+self.alter_c[i].c + \
                    f',{self.alter_c[i].tol})\n\t\t'
    for i in range(self.lengthr):
        loop = loop+'alter ' + \
            self.alter_r[i].name + \
            '=unif('+self.alter_r[i].r + \
                    f',{self.alter_r[i].tol})\n\t\t'

    loop = loop+'print '
    for i in range(self.lengthc):
        loop = loop+f'@{self.alter_c[i].name}[capacitance] '
    for i in range(self.lengthr):
        loop = loop+f'@{self.alter_r[i].name}[resistance] '
    loop = loop+'>> paramlist\n\t\t'

    if self.measmode == 'Cutoff Frequency':
        self.control.append(
            f'ac dec 40 {self.startac} {self.stopac}\n\n\t\tmeas ac ymax MAX v({self.netselect})\n\t\tlet v3db = ymax/sqrt(2)\n\t\tmeas ac cut when v({self.netselect})=v3db {self.rfmode}\n\t\tlet {{$scratch}}.cutoff[run] = cut\n\t\tdestroy $curplot\n\t\tlet run = run + 1\n\tend\n\n\tsetplot $scratch\n\t')

    else:
        self.control.append(
            f'ac dec 40 {self.startac} {self.stopac}\n\n\t\tmeas ac y{self.measmode} {self.measmode} v({self.netselect})\n\t\tlet {{$scratch}}.cutoff[run] = y{self.measmode}\n\t\tdestroy $curplot\n\t\tlet run = run + 1\n\tend\n\n\tsetplot $scratch\n\t')

    self.control.append('wrdata fc cutoff\n.endc\n\n.end')

    with open('run_control.sp', 'w') as file_object:
        file_object.write(self.control[0])
        file_object.write(loop)
        file_object.write(self.control[1])
        file_object.write(self.control[2])


def create_wst(self):
    self.wst_run = 2**(self.lengthc+self.lengthr)

    control = [
        f"*ng_script\n\n.control\n\tdestroy all\n\tset wr_vecnames\n\tunlet run mc_runs\n\tunset appendwrite\n\tdefine binary(run,index) floor(run/(2^index))-2*floor(run/(2^index+1))\n\tdefine wc(nom,tol,index,run,numruns) (run >= numruns) ? nom : (binary(run,index) ? nom*(1+tol) : nom*(1-tol))\n\n\tsource run.cir\n\tsave {self.netselect}\n\tlet numruns = {self.wst_run}\n\tlet run = 0\n\tset curplot=new          $ create a new plot\n\tset scratch=$curplot     $ store its name to 'scratch'\n\tlet cutoff=unitvec(numruns+1)\n"]
    loop = '\tdowhile run <= numruns\n\t\t'

    for i in range(self.lengthc):
        loop = loop+'alter ' + \
            self.alter_c[i].name+'=wc('+self.alter_c[i].c + \
            f',{self.alter_c[i].tol},{i},run,numruns)\n\t\t'
    for i in range(self.lengthr):
        loop = loop+'alter ' + \
            self.alter_r[i].name + \
            '=wc('+self.alter_r[i].r + \
            f',{self.alter_r[i].tol},{i+self.lengthc},run,numruns)\n\t\t'

    with open('run_control_wst.sp', 'w') as file_object:
        file_object.write(control[0])
        file_object.write(loop)
        file_object.write(self.control[1])
        file_object.write('wrdata fc_wst cutoff\n.endc\n\n.end')
