import os
import shutil
import subprocess
from datetime import datetime

# path=os.getcwd()+'/Workspace/bin'
# os.environ['PATH']+=':'+path
# print(os.environ['PATH'])
# os.system('ngspice')
home=os.path.expanduser('~')

x=os.chdir(home)
# os.chdir('Workspace/')
print(os.getcwd())
# os.chdir('..')
# print(os.getcwd())
# dir='Workspace/'+datetime.now().strftime("%d%m%Y_%H%M%S")+'/'
# os.mkdir(dir)
# shutil.copyfile('main.py',dir+'main')
# print(os.path.isfile('test/main'))
'''
with open('test.cir','r+') as a:
    text=a.read()
    text=text.replace('include','.inc')
    print(text)
'''

# proc=subprocess.Popen('ngspice -b test.cir -o test.log',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
# proc=subprocess.Popen('ngspice -b test.cir -o test.log',shell=True,stderr=subprocess.PIPE)
# _,stderr=proc.communicate()
# stderr=stderr.decode('ASCII')
# print(proc.returncode)
# # print('STDOUT: ',stdout)
# print('STDERR: ',stderr.encode('unicode_escape').decode('ASCII'),type(stderr))
# if stderr:
#     print('Something')