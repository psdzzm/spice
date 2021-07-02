# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 30-06-2021 18:56:02
 LastEditors: Yichen Zhang
 LastEditTime: 02-07-2021 01:06:08
 FilePath: /circuit/src/is3.py
'''

import numpy as np
from scipy import interpolate
from matplotlib import pyplot as plt
import hashlib
import os
import logging

# home = os.path.expanduser('~')
# md=hashlib.md5(open(home+'/.spiceinit','rb').read()).hexdigest()
# print(md)
logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler("log.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)

logger.addHandler(handler)
logger.addHandler(console)

logger.info("Start print log")
logger.debug("Do something")
logger.warning("Something maybe fail.")
logger.info("Finish")

x=np.random.rand(10)
y=np.random.rand(10)*10
# print(x)
index=x.argsort()
x=np.array([1,2,3,4,5,5,6,7,8,9])
y.sort()
print(y)
z,index2=np.unique(x,return_index=True)
print(z,index2)
fit=interpolate.interp1d(x,y,kind='linear')
plt.plot(x,fit(x),x,y)

plt.show()
# xx=[10,3,5,7,9,2,3,5,7,11]

# for i in range(10):
#     # print(xx[index[0:i+1]])
#     print(index[0:i+1])

# a=np.array([2,3])
# b=np.array([5,6])
# c=a*b
# print(c)

# x=[]
# x=np.append(x,[0,1,2,3])
# print(x)