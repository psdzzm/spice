import os
import shutil
import subprocess

# x=os.chdir('./CirFile')
os.chdir('Workspace/')
# shutil.copyfile('main.py','/home/zyc/Desktop/projects/circuit/test/main')
# print(os.path.isfile('test/main'))
'''
with open('test.cir','r+') as a:
    text=a.read()
    text=text.replace('include','.inc')
    print(text)
'''

# proc=subprocess.Popen('ngspice -b test.cir -o test.log',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
proc=subprocess.Popen('ngspice -b test.cir -o test.log',shell=True,stderr=subprocess.PIPE)
_,stderr=proc.communicate()
stderr=stderr.decode('ASCII')
print(proc.returncode)
# print('STDOUT: ',stdout)
print('STDERR: ',stderr.encode('unicode_escape').decode('ASCII'),type(stderr))
if stderr:
    print('Something')