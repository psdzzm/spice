# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 02-07-2021 22:14:06
 LastEditors: Yichen Zhang
 LastEditTime: 12-07-2021 15:01:28
 FilePath: /circuit/src/isf.py
'''
import subprocess


xyz=5
def try2():
    print('isf loaded')

import readline

def rlinput(prompt, prefill=''):
   readline.set_startup_hook(lambda: readline.insert_text(prefill))
   try:
      return input(prompt)  # or raw_input in Python 2
   finally:
      readline.set_startup_hook()

x=rlinput('Please enter times:','100')
print(x)
