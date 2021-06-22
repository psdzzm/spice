import os
import shutil

# x=os.chdir('./CirFile')
print(os.getcwd())
# shutil.copyfile('main.py','/home/zyc/Desktop/projects/circuit/Workspace/main.py')
if os.path.isfile('src/read.py'):
    print('Exist')
else:
    print('Not exist')

os.chdir(os.path.dirname('src/read.py'))
print(os.getcwd())
