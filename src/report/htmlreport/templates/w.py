# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 12-07-2021 01:20:27
 LastEditors: Yichen Zhang
 LastEditTime: 12-07-2021 01:21:32
 FilePath: /circuit/src/report/htmlreport/templates/w.py
'''
from weasyprint import HTML
import os

os.chdir(os.path.dirname(__file__))
with open('report.html') as f:
    html=HTML(string=f.read())

html.write_pdf('report.pdf')