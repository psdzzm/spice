# Read Circuit File
import os
import shutil
import subprocess
import time
import re
import numpy as np
from matplotlib import pyplot as plt
import operator
from src.runspice import runspice


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


class C:
    def __init__(self, name, c, tol=0.05):
        self.name = name
        self.c = c
        self.tol = tol


class circuit:
    def __init__(self, filename):
        self.name = filename
        self.seed = int(time.time())
        self.mc_runs = 1000
        self.tolc = 0.05
        self.tolr = 0.01
        self.adjust = False

        self.workpath = '/home/zyc/Desktop/projects/circuit/Workspace/lib/'

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
                    filename = row[1].split('/')[-1].split('.')[0].upper()
                    path2check = self.workpath+'usr/'+filename  # Only file name without extension
                    # Directory lib has include file
                    if os.path.isfile(self.workpath+filename):
                        lines = '.include ../lib/'+filename+'\n'
                    # Source Directory has
                    elif os.path.isfile(row[1]):
                        lines = '.include ../lib/usr/'+filename+'\n'
                        shutil.copyfile(row[1], path2check)
                        print('Copy '+row[1]+' to '+path2check)
                    else:           # Directory ../lib/usr has include file or will be later copied to
                        lines = '.include ../lib/usr/'+filename+'\n'

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

        control = '\n.control\n\toptions appendwrite wr_singlescale\n\tshow r : resistance , c : capacitance > list\n\tOP\n\tdisplay all > netlist\n\twrdata out out\n\tac dec 40 1 1G\n\tmeas ac ymax MAX v(out)\n\tmeas ac fmax MAX_AT v(out)\n\tlet v3db = ymax/sqrt(2)\n\tmeas ac cut when v(out)=v3db fall=last\n\twrdata out fmax cut vdb(out)\n.endc\n'
        with open('test.cir', 'w') as file_object, open('run.cir', 'w') as b:
            if start and stop1:
                file_object.write(''.join(fileo[0:start]))
                file_object.write(control)
                file_object.write(''.join(fileo[stop1+1:stop2+1]))

                b.write(''.join(fileo[0:start]))
                b.write(''.join(fileo[stop1+1:stop2+1]))

            else:
                file_object.write(''.join(fileo[0:stop2]))
                file_object.write(control)
                file_object.write('.end')

                b.write(''.join(fileo[0:stop2]))
                b.write('.end')

    def fixinclude(self, repl, mode):
        with open('test.cir', 'r+') as file_object, open('run.cir', 'r+') as b:
            test = file_object.read()
            run = b.read()
            if mode == 1:     # Include error
                test = test.replace('.include ../lib/usr/'+self.subckt,
                                    '.include ../lib/usr/'+repl)
                run = run.replace('.include ../lib/usr/'+self.subckt,
                                  '.include ../lib/usr/'+repl)
            elif mode == 2:   # Subcircuit error
                test = test.replace(
                    '.control\n', '.include ../lib/usr/'+repl+'\n.control\n')
                run = run[:-4]+'.include ../lib/usr/'+repl+'\n.end'

            file_object.seek(0)
            file_object.write(test)

            b.seek(0)
            b.write(run)

        return self.init()

    def init(self):
        rm('out')
        rm('run.log')
        print('\nChecking if the input circuit is valid.\n')
        # if not os.path.isfile('.spiceinit'):
        #     with open('.spiceinit', 'w') as f:
        #         f.write('* User defined ngspice init file\n\n    set filetype=ascii\n\tset color0=white\n\tset wr_vecnames\t\t$ wrdata: scale and data vector names are printed on the first row\n\t*set wr_singlescale\t$ the scale vector will be printed only once\n\n* unif: uniform distribution, deviation relativ to nominal value\n* aunif: uniform distribution, deviation absolut\n* gauss: Gaussian distribution, deviation relativ to nominal value\n* agauss: Gaussian distribution, deviation absolut\n* limit: if unif. distributed value >=0 then add +avar to nom, else -avar\n\n\tdefine unif(nom, rvar) (nom + (nom*rvar) * sunif(0))\n\tdefine aunif(nom, avar) (nom + avar * sunif(0))\n\tdefine gauss(nom, rvar, sig) (nom + (nom*rvar)/sig * sgauss(0))\n\tdefine agauss(nom, avar, sig) (nom + avar/sig * sgauss(0))\n\tdefine limit(nom, avar) (nom + ((sgauss(0) >= 0) ? avar : -avar))\n')
        # os.system("ngspice -b test.cir -o test.log")
        proc = subprocess.Popen(
            'ngspice -b test.cir -o test.log', shell=True, stderr=subprocess.PIPE)
        _, stderr = proc.communicate()
        if stderr:
            return stderr.decode('ASCII')+'Please check if the netlist file or include file is valid', False

        with open('test.log') as file_object:
            fileo = file_object.readlines()
            error_r = []
            i = 0
            flag = 0
            while i < len(fileo):
                if fileo[i].lower().startswith('error'):
                    if fileo[i] == 'Error: no data saved for D.C. Operating point analysis; analysis not run\n':
                        return "Error! No 'out' port!", flag
                    elif fileo[i] == 'Error: measure  cut  (WHEN) : out of interval\n':
                        return "Error! No AC stimulus found or cutoff frequency out of range:\nSet the value of a current or voltage source to 'AC 1.'to make it behave as a signal generator for AC analysis.", flag
                    elif 'Could not find include file' in fileo[i]:
                        self.subckt = fileo[i].split(
                        )[-1].replace('../lib/usr/', '').rstrip()
                        fileo[i] = fileo[i].replace('../lib/usr/', '') + \
                            f"Please provide the simulation model file for {self.subckt}\n"
                        flag = 1    # Include Error
                    elif 'unknown subckt' in fileo[i]:
                        self.subckt = fileo[i].split(
                        )[-1].replace('../lib/usr/', '').rstrip().upper()
                        fileo[i] = fileo[i].replace('../lib/usr/', '') + \
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

        with open('out') as file_object:
            self.startac, self.stopac = 0, 0
            fileo, files,self.initx,self.inity = [], [],[],[]
            for lines in file_object:
                fileo.append(lines)
                files.append(lines.split())
                if 'fmax' in files[-1] and 'cut' in files[-1]:
                    fileo.append(file_object.readline())
                    files.append(fileo[-1].split())
                    self.startac = files[-1][files[-2].index('fmax')]
                    self.stopac = files[-1][files[-2].index('cut')]
                    self.initx.append(float(files[-1][0]))
                    self.inity.append(float(files[-1][-1]))
                    for lines in file_object:
                        temp=lines.split()
                        self.initx.append(float(temp[0]))
                        self.inity.append(float(temp[-1]))
                    break
            if self.startac == 0 and self.stopac == 0:
                return 'Error! No cutoff frequecny!', flag
            else:
                print('Check successfully! Running simulation.\n')

        with open('list') as file_object:
            self.alter_r = []
            self.alter_c = []
            fileo, files = [], []
            for lines in file_object:
                row = lines.split()
                fileo.append(lines)
                files.append(row)

            # print(files)
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

        return flag, flag

    def readnet(self):
        with open('netlist') as file_object:
            file=file_object.readlines()
            self.net=[]
            for line in file:
                if 'voltage,' in line:
                    start=line.split()[0]
                    if not re.match(r'x[\d\w]+\.',start):
                        m=re.match(r'V\((\d+)\)',start)
                        if m:
                            self.net.append(m.group(1))
                        else:
                            self.net.append(start)
        self.net.remove('out')
        self.net.sort()


    def create_sp(self):
        self.seed = int(time.time())

        self.control = [
            f"*ng_script\n\n.control\n\tsource run.cir\n\tsave {self.netselect}\n\tlet mc_runs = {self.mc_runs}\n\tlet run = 0\n\tset curplot=new          $ create a new plot\n\tset scratch=$curplot     $ store its name to 'scratch'\n\tlet cutoff=unitvec(mc_runs)\n\tsetseed {self.seed}\n\n"]
        loop = '\tdowhile run < mc_runs\n\t\t'

        if self.adjust:
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
        else:
            for i in range(self.lengthc):
                loop = loop+'alter ' + \
                    self.alter_c[i].name + \
                    '=gauss('+self.alter_c[i].c+f',{self.tolc},3)\n\t\t'
            for i in range(self.lengthr):
                loop = loop+'alter ' + \
                    self.alter_r[i].name + \
                    '=gauss('+self.alter_r[i].r+f',{self.tolr},3)\n\t\t'


        if self.measmode=='Cutoff Frequency':
            if self.risefall:
                rfmode='fall='
            else:
                rfmode='rise='
            if self.rfnum==0:
                rfmode=rfmode+'last'
            else:
                rfmode=rfmode+str(self.rfnum)

            self.control.append(f'ac dec 40 {float(self.startac)/10} {float(self.stopac)*10}\n\n\t\tmeas ac ymax MAX v({self.netselect})\n\t\tlet v3db = ymax/sqrt(2)\n\t\tmeas ac cut when v({self.netselect})=v3db {rfmode}\n\t\tlet {{$scratch}}.cutoff[run] = cut\n\t\tlet run = run + 1\n\tend\n\n\tsetplot $scratch\n\t')

        else:
            self.control.append(f'ac dec 40 {float(self.startac)/10} {float(self.stopac)*10}\n\n\t\tmeas ac y{self.measmode} {self.measmode} v({self.netselect})\n\t\tlet {{$scratch}}.cutoff[run] = y{self.measmode}\n\t\tlet run = run + 1\n\tend\n\n\tsetplot $scratch\n\t')

        self.control.append('wrdata fc cutoff\n.endc\n\n.end')

        with open('run_control.sp', 'w') as file_object:
            file_object.write(self.control[0])
            file_object.write(loop)
            file_object.write(self.control[1])
            file_object.write(self.control[2])


    def create_wst(self):
        self.wst_run = 2**(self.lengthc+self.lengthr)

        control = [
            f"*ng_script\n\n.control\n\tdefine binary(run,index) floor(run/(2^index))-2*floor(run/(2^index+1))\n\tdefine wc(nom,tol,index,run,numruns) (run >= numruns) ? nom : (binary(run,index) ? nom*(1+tol) : nom*(1-tol))\n\n\tsource run.cir\n\tsave {self.netselect}\n\tlet numruns = {self.wst_run}\n\tlet run = 0\n\tset curplot=new          $ create a new plot\n\tset scratch=$curplot     $ store its name to 'scratch'\n\tlet cutoff=unitvec(numruns+1)\n"]
        loop = '\tdowhile run <= numruns\n\t\t'

        if self.adjust:
            for i in range(self.lengthc):
                loop = loop+'alter ' + \
                    self.alter_c[i].name+'=wc('+self.alter_c[i].c + \
                    f',{self.alter_c[i].tol},{i},run,numruns)\n\t\t'
            for i in range(self.lengthr):
                loop = loop+'alter ' + \
                    self.alter_r[i].name + \
                    '=wc('+self.alter_r[i].r + \
                    f',{self.alter_r[i].tol},{i+self.lengthc},run,numruns)\n\t\t'
        else:
            for i in range(self.lengthc):
                loop = loop+'alter ' + \
                    self.alter_c[i].name+'=wc('+self.alter_c[i].c + \
                    f',{self.tolc},{i},run,numruns)\n\t\t'
            for i in range(self.lengthr):
                loop = loop+'alter ' + \
                    self.alter_r[i].name + \
                    '=wc('+self.alter_r[i].r + \
                    f',{self.tolr},{i+self.lengthc},run,numruns)\n\t\t'

        with open('run_control_wst.sp', 'w') as file_object:
            file_object.write(control[0])
            file_object.write(loop)
            file_object.write(self.control[1])
            file_object.write('wrdata fc_wst cutoff\n.endc\n\n.end')


    def ngspice(self, mode=0):
        runspice(mode)


    _col2 = []
    wst_cutoff = []
    def resultdata(self, appnd=False, worst=True):
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
