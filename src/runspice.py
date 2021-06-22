from timeit import default_timer as timer
import os
from datetime import datetime

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
    runspice()