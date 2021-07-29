# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 29-07-2021 17:11:28
 LastEditors: Yichen Zhang
 LastEditTime: 29-07-2021 18:52:21
 FilePath: /spice/Workspace/Audio_AmpV3 29072021_164433/res.py
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
            result[i] = temp[index]
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

nan = np.isnan(result)
sub = np.split(result[np.logical_not(nan)], np.where(nan)[0])
freq = freq[0:len(sub[0])]
result = np.zeros([len(sub), len(sub[0])])
for i in range(len(sub)):
    result[i] = 20 * np.log10(np.abs(sub[i]))

print(np.shape(result)[0])
# plt.show()
