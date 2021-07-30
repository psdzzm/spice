# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 29-07-2021 17:11:28
 LastEditors: Yichen Zhang
 LastEditTime: 30-07-2021 17:32:05
 FilePath: /spice/Workspace/Audio_AmpV3 30072021_161501/res.py
'''
import os
import numpy as np
from matplotlib import pyplot as plt

os.chdir(os.path.dirname(__file__))
with open('fc', 'r') as fileobject:
    title = fileobject.readline().split()
    data = fileobject.readlines()

print(title)
net = 'out'
if net.isdigit():
    index = [i for i, x in enumerate(title) if x == 'V(' + net + ')']  # Get index of all selected net data
else:
    index = [i for i, x in enumerate(title) if x == net]

i = 0
freq = np.zeros(len(data))
result = np.zeros(len(data), dtype=np.complex_)
if len(index) == 1:
    for line in data:
        temp = line.split()
        try:
            freq[i] = temp[0]
            result[i] = temp[index[0]]
        except ValueError:
            result[i] = np.NaN
        i += 1
else:
    for line in data:
        temp = line.split()
        try:
            freq[i] = temp[0]
            result[i] = float(temp[index[0]]) + float(temp[index[1]]) * 1j
        except ValueError:
            result[i] = np.NaN
        i += 1

notnan = np.where(np.logical_not(np.isnan(result)))[0]
loc = np.where(np.diff(notnan) != 1)[0] + 1
sub = np.split(result[notnan], loc)
freq = np.split(freq[notnan], loc)
length = 0
for i in range(len(sub)):
    length = max(length, len(sub[i]))
resultx = np.full([len(sub), length], np.inf)
resulty = np.full([len(sub), length], np.inf)
for i in range(len(sub)):
    resultx[i, 0:len(freq[i])] = freq[i]
    if title[0] == 'frequency':
        resulty[i, 0:len(sub[i])] = 20 * np.log10(np.abs(sub[i]))
    else:
        resulty[i, 0:len(sub[i])] = sub[i].real
    print(resultx[i], resulty[i], sep='\n')
    plt.plot(resultx[i], resulty[i])

plt.show()
