# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 30-06-2021 13:20:17
 LastEditors: Yichen Zhang
 LastEditTime: 30-06-2021 21:17:37
 FilePath: /circuit/src/is2.py
'''
from math import sin
from numpy.ma.core import sqrt
from scipy import stats
from scipy.special import erf
from scipy.integrate import quad
import numpy as np
from matplotlib import pyplot as plt

th = 3
def h(x): return (x-2000)**3-(x-1990)**2


tol = 0.01
miu = 2000
sigma = miu*tol/3


def f(x, miu=2000, sigma=1, tol=0.01):
    return np.exp(-1/2*((x-miu)/sigma)**2)/(sigma*np.sqrt(2*np.pi)*(erf(tol*miu/sigma/np.sqrt(2))-erf(-tol*miu/sigma/np.sqrt(2)))/2)


def rv(miu=2000, tol=0.01):
    return stats.uniform(miu*(1-tol), 2*miu*tol)

# fx = lambda x : np.exp(-x**2/2/sigma**2)/(erf(tol/np.sqrt(2))*sigma*np.sqrt(2*np.pi))
# rv=stats.uniform(miu*(1-tol),2*miu*tol)
# g = lambda x : rv.pdf(x)


N = 1000000

nor = stats.norm(loc=miu, scale=sigma)
yxx = h(nor.rvs(size=N))
yxx.sort()
plt.plot(yxx, np.linspace(-1, 0, N))


X = rv().rvs(size=N)
X.sort()
Y = h(X)
yy = np.copy(Y)
index = yy.argsort()
yy.sort()
m2 = np.zeros(N)
t = f(X, miu, sigma, tol)/rv(miu, tol).pdf(X)
seq = 0
for i in range(N):
    seq += t[index[i]]
    m2[i] = 1/N*seq
# plt.plot(X,np.ones(N),'xr')
# m2=X[X>th]

# m2=(m2-m2[0])/(m2[-1]-m2[0])

# plt.plot(X,f(X,miu,sigma,tol))
plt.plot(yy, m2)
plt.grid()

print(quad(lambda x: np.exp(-1/2*((x-miu)/sigma)**2)/(sigma*np.sqrt(2*np.pi) *
      (erf(tol*miu/sigma/np.sqrt(2))-erf(-tol*miu/sigma/np.sqrt(2)))/2), 1980, 2020))

plt.show()
