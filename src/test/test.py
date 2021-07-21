# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 11-07-2021 16:44:39
 LastEditors: Yichen Zhang
 LastEditTime: 11-07-2021 19:07:17
 FilePath: /spice/src/test.py
'''

from django.template.loader import render_to_string
from django.template import Context, Template
import django
import os,sys



if __name__=='__main__':
    os.chdir(os.path.dirname(__file__)+'/report')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'report.settings')
    sys.path.append(os.path.dirname(__file__)+'/report')
    django.setup()
    # os.chdir("htmlreport/templates/")
    # print(os.listdir())
    with open('/home/zyc/Desktop/projects/spice/src/report/htmlreport/templates/inherit.html') as f:
        t=Template(f.read())

    context=Context()
    print(t.render(context))
    # rendered=render_to_string('/home/zyc/Desktop/projects/spice/src/report/htmlreport/templates/inherit.html')
    # with open('rendered.html','w') as r:
    #     r.write(rendered)