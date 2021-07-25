# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 26-06-2021 14:43:04
 LastEditors: Yichen Zhang
 LastEditTime: 27-06-2021 18:28:15
 FilePath: /circuit/Workspace/test/netlist.py
'''
import re
import os

os.chdir(os.path.dirname(__file__))
with open('op') as file_object:
    nets=list(set(file_object.readline().split()))
    print(len(nets))
    net=[]
    port=[]
    for item in nets[1:]:
        if '#branch' in item:
            continue
        else:
            net.append(item)
            temp=re.match(r'x[\d\w]+\.',item)
            print(temp)
            if not temp:
                m=re.match(r'V\((\d+)\)',item)
                if m:
                    port.append(m.group(1))
                else:
                    port.append(item)

    print(net,'\n',port)