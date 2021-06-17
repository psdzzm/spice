from matplotlib import pyplot as plt
import matplotlib
import numpy as np
import os
os.system("ngspice -b LPF.cir")
with open('lpf', "r") as fileobject:
    lines=fileobject.readlines()
file1=[]
row=[]
for line in lines:
    row=line.split()
    file1.append(row)

col1=[]
col2=[]
for row0 in file1:
    col1.append(row0[0])
    col2.append(row0[1])

del col1[0]
del col2[0]

length=len(col1)
cout=np.zeros(length)
cutoff=np.zeros(length)

for i in range(length):
    cout[i]=float(col1[i])
    cutoff[i]=float(col2[i])

index=cutoff.argsort()
print(cutoff[index])

# fig=plt.figure()
# ax=plt.gca()
# mkfunc = lambda x, pos: '%1.1fM' % (x * 1e-6) if x >= 1e6 else '%1.1fK' % (x * 1e-3) if x >= 1e3 else '%1.1f' % x
# mkformatter = matplotlib.ticker.FuncFormatter(mkfunc)
# ax.yaxis.set_major_formatter(mkformatter)
plt.title("Cutoff Frequency for Different C")
plt.xlabel("Probablity")
plt.ylabel("Cutoff Frequency/Hz")
plt.grid()
plt.plot(cutoff[index],np.arange(1,1+length)/length)
plt.show()