# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 30-06-2021 18:56:02
 LastEditors: Yichen Zhang
 LastEditTime: 30-06-2021 21:38:06
 FilePath: /circuit/src/is3.py
'''

import numpy as np

x=np.random.rand(10)
print(x)
index=x.argsort()
xx=[10,3,5,7,9,2,3,5,7,11]

for i in range(10):
    # print(xx[index[0:i+1]])
    print(index[0:i+1])

a=np.array([2,3])
b=np.array([5,6])
c=a*b
print(c)