# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 12-07-2021 01:20:27
 LastEditors: Yichen Zhang
 LastEditTime: 12-07-2021 19:01:00
 FilePath: /circuit/src/report/htmlreport/templates/w.py
'''
# from weasyprint import HTML
import os
from html5print import HTMLBeautifier

# os.chdir(os.path.dirname(__file__))
with open('report.html') as f:
    h=f.read()
    # html=HTML(string=h)
    print(HTMLBeautifier.beautify(h,4))

# html.write_pdf('report.pdf')