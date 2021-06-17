import os,time
from timeit import default_timer as timer
from read import rm




def ngspice():
    rm('fc')
    start=timer()
    os.system('ngspice -b run_control.sp -o run_log')
    print('Time elapsed:', timer()-start,'s')