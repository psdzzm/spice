# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 12-07-2021 01:20:27
 LastEditors: Yichen Zhang
 LastEditTime: 14-07-2021 01:10:52
 FilePath: /circuit/src/report/htmlreport/templates/w.py
'''
# from weasyprint import HTML
import os
from bs4 import BeautifulSoup

os.chdir(os.path.dirname(__file__))
with open('report.html') as f:
    h = f.read()
    # html=HTML(string=h)
    soup = BeautifulSoup(h)
    # print(HTMLBeautifier.beautify(h,4))
    print(BeautifulSoup(h).prettify())

# html.write_pdf('report.pdf')
