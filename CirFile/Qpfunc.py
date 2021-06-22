from timeit import default_timer as timer
import os
import numpy as np
import sys


length=1
time=np.zeros(length)
for i in range(length):
    start=timer()
    os.system('ngspice -b run_control.sp -o run.log')
    time[i]=timer()-start
    print(time[i])

print(time)
print(np.mean(time))