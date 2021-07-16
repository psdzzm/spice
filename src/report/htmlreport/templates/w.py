# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 12-07-2021 01:20:27
 LastEditors: Yichen Zhang
 LastEditTime: 16-07-2021 15:55:15
 FilePath: /circuit/src/report/htmlreport/templates/w.py
'''
# from weasyprint import HTML
import os
from bs4 import BeautifulSoup

os.chdir(os.path.dirname(__file__))
with open('report.html') as f:
    h = f.read()
    with open('inherit.html') as f2:
        print(f2.readline())
    # html=HTML(string=h)
    soup = BeautifulSoup(h)
    # print(HTMLBeautifier.beautify(h,4))
    print(BeautifulSoup(h).prettify())

# html.write_pdf('report.pdf')
