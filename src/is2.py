# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 30-06-2021 13:20:17
 LastEditors: Yichen Zhang
 LastEditTime: 30-06-2021 21:44:40
 FilePath: /circuit/src/is2.py
'''

from numpy.ma.core import sqrt
from scipy import stats
from scipy.special import erf
from scipy.integrate import quad
import numpy as np
from matplotlib import pyplot as plt

th = 3
def h(x,y):
    # return (x-2000)**3-(x-1990)**2
    return x-2*y


tolx = 0.01
miux = 2000
sigmax = miux*tolx/3
toly=0.05
miuy=100
sigmay=miuy*toly/3

def f(x, miu=2000, sigma=1, tol=0.01):
    return np.exp(-1/2*((x-miu)/sigma)**2)/(sigma*np.sqrt(2*np.pi)*(erf(tol*miu/sigma/np.sqrt(2))-erf(-tol*miu/sigma/np.sqrt(2)))/2)


def rv(miu=2000, tol=0.01):
    return stats.uniform(miu*(1-tol), 2*miu*tol)

# fx = lambda x : np.exp(-x**2/2/sigma**2)/(erf(tol/np.sqrt(2))*sigma*np.sqrt(2*np.pi))
# rv=stats.uniform(miu*(1-tol),2*miu*tol)
# g = lambda x : rv.pdf(x)


N = 1000

norx = stats.norm(loc=miux, scale=sigmax)
nory=stats.norm(loc=miuy, scale=sigmay)
yxy = h(norx.rvs(size=N),nory.rvs(size=N))
yxy.sort()
plt.plot(yxy, np.linspace(-1, 0, N))


X = rv(miux,tolx).rvs(size=N)
Y=rv(miuy,toly).rvs(size=N)

Z = h(X,Y)
zz = np.copy(Z)
index = zz.argsort()
zz.sort()   # For plot in order
m2 = np.zeros(N)
tx = f(X, miux, sigmax, tolx)/rv(miux, tolx).pdf(X)
ty=f(Y, miuy, sigmay, toly)/rv(miuy, toly).pdf(Y)
txy=tx*ty
seq = 0
for i in range(N):
    seq += txy[index[i]]
    m2[i] = 1/N*seq
# plt.plot(X,np.ones(N),'xr')
# m2=X[X>th]

m2=(m2-m2[0])/(m2[-1]-m2[0])

print(m2[0],m2[-1])
plt.plot(zz, m2)
plt.grid()

print(quad(lambda x: np.exp(-1/2*((x-miux)/sigmax)**2)/(sigmax*np.sqrt(2*np.pi) *
      (erf(tolx*miux/sigmax/np.sqrt(2))-erf(-tolx*miux/sigmax/np.sqrt(2)))/2), 1980, 2020))

plt.show()
