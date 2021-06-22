from timeit import default_timer as timer
import os,sys
from datetime import datetime
import getopt

def rm(filename):
    try:
        os.remove(filename)
    except OSError:
        pass

def runspice(mode=0):
    start=timer()
    if mode:
        rm('fc_wst')
        os.system('ngspice -b run_control_wst.sp -o run_log')
    else:
        rm('fc')
        os.system('ngspice -b run_control.sp -o run_log')
    print(f'Time elapsed: {timer()-start}s')
    with open('run.log','a') as a, open('run_log') as b:
        data=b.read()
        a.write('Creation Date: '+datetime.now().strftime("%d/%m/%Y %H:%M:%S\n"))
        a.write(data)
    rm('run_log')

if __name__ == "__main__":
    opts,args=getopt.getopt(sys.argv[1:],'012')
    if opts==[]:
        runspice()
    elif opts[0][0]=='-0':
        runspice(0)
    elif opts[0][0]=='-1':
        runspice(1)
    elif opts[0][0]=='-2':
        runspice(0)
        runspice(1)

