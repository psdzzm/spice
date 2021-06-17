# Read Circuit File
import os
import sys
import time


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
    def __init__(self, name, r):
        self.name = name
        self.r = r


class C:
    def __init__(self, name, c):
        self.name = name
        self.c = c


class circuit:
    def __init__(self, filename):
        self.name = filename
        self.startac, self.stopac, self.alter_c, self.alter_r = self.init()
        self.seed = int(time.time())
        self.mc_run = 1000
        self.tolc = 0.05
        self.tolr = 0.01

    def read(self):
        fileo, files = [], []
        start, stop1, stop2 = 0, 0, 0
        matches = ['.model', '.subckt', '.global', '.include', '.lib',
                   '.param', '.func', '.temp', '.control', '.endc', '.end']
        with open(self.name) as file_object:
            for lines in file_object:
                row = lines.split()
                if row != [] and row[0].lower() not in matches and '.' in row[0].lower():
                    continue
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
            sys.exit("No 'end' line!")

        control = '\n.control\n\tSAVE out\n\toptions appendwrite wr_singlescale\n\tshow r : resistance , c : capacitance > list\n\tOP\n\twrdata out out\n\tac dec 40 1 1G\n\tmeas ac ymax MAX v(out)\n\tmeas ac fmax MAX_AT v(out)\n\tlet v3db = ymax/sqrt(2)\n\tmeas ac cut when v(out)=v3db fall=last\n\twrdata out fmax cut\n.endc\n'
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

    def init(self):
        rm('out')
        print('\nChecking if the input circuit is valid.\n')
        os.system("ngspice -b test.cir -o test_log")
        with open('test_log') as file_object:
            fileo = file_object.readlines()
            error_r = []
            i = 0
            while i < len(fileo):
                if fileo[i].lower().startswith('error'):
                    if fileo[i] == 'Error: no data saved for D.C. Operating point analysis; analysis not run\n':
                        sys.exit("Error! No 'out' port!")
                    elif fileo[i] == 'Error: measure  cut  (WHEN) : out of interval\n':
                        sys.exit("Error! No AC stimulus found or cutoff frequency out of range:\nSet the value of a current or voltage source to 'AC 1.'to make it behave as a signal generator for AC analysis.")
                    elif 'fatal error' in fileo[i]:
                        sys.exit(f'{fileo[i]}')

                    error_r.append(fileo[i])
                    i += 1
                    while fileo[i].startswith('  '):
                        error_r.append(fileo[i])
                        i += 1
                else:
                    i += 1

            if error_r:
                sys.exit(''.join(error_r))

        with open('out') as file_object:
            startac, stopac = 0, 0
            fileo, files = [], []
            for lines in file_object:
                fileo.append(lines)
                files.append(lines.split())
                if 'fmax' in files[-1] and 'cut' in files[-1]:
                    fileo.append(file_object.readline())
                    files.append(fileo[-1].split())
                    startac = files[-1][files[-2].index('fmax')]
                    stopac = files[-1][files[-2].index('cut')]
                    break
            if startac == 0 and stopac == 0:
                sys.exit('Error! No cutoff frequecny!')
            else:
                print('Check successfully! Running simulation.\n')

        with open('list') as file_object:
            alter_r = []
            alter_c = []
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
                        if '.' not in files[i][j]:
                            if files[i+2][0] == 'resistance':
                                alter_r.append(R(files[i][j], files[i+2][j]))
                            elif files[i+2][0] == 'capacitance':
                                alter_c.append(C(files[i][j], files[i+2][j]))

            # for i in range(len(alter_r)):
            #     print(alter_r[i].name,alter_r[i].r,'\n')
            # for i in range(len(alter_c)):
            #     print(alter_c[i].name,alter_c[i].c,'\n')

            return startac, stopac, alter_c, alter_r

    def create_sp(self):

        control = [
            f"*ng_script\n\n.control\n\tsource run.cir\n\tsave out\n\tlet mc_runs = {mc_runs}\n\tlet run = 0\n\tset curplot=new          $ create a new plot\n\tset scratch=$curplot     $ store its name to 'scratch'\n\tlet cutoff=unitvec(mc_runs)\n\tsetseed {self.seed}\n\n"]
        loop = '\tdowhile run < mc_runs\n\t\t'

        for i in range(len(self.alter_c)):
            loop = loop+'alter ' + \
                self.alter_c[i].name+'=gauss('+self.alter_c[i].c+f',{tolc},3)\n\t\t'
        for i in range(len(self.alter_r)):
            loop = loop+'alter ' + \
                self.alter_r[i].name + \
                '=gauss('+self.alter_r[i].r+f',{tolr},3)\n\t\t'

        control.append(
            f'ac dec 40 {float(self.startac)/10} {float(self.stopac)*10}\n\n\t\tmeas ac ymax MAX v(out)\n\t\tlet v3db = ymax/sqrt(2)\n\t\tmeas ac cut when v(out)=v3db fall=last\n\t\tlet {{$scratch}}.cutoff[run] = cut\n\t\tlet run = run + 1\n\tend\n\n\tsetplot $scratch\n\twrdata fc cutoff\n.endc\n')

        with open('run_control.sp', 'w') as file_object:
            file_object.write(control[0])
            file_object.write(loop)
            file_object.write(control[1])
            file_object.write('\n.end')
