import re
import os

os.chdir('CirFile')
with open('netlist') as file_object:
    file=file_object.readlines()
    net=[]
    for line in file:
        if 'voltage,' in line:
            start=line.split()[0]
            net.append(start)
            temp=re.match(r'x[\d\w]+\.',start)
            print(temp)
            if not temp:
                m=re.match(r'V\((\d+)\)',start)
                if m:
                    print('Matched Net:',m.group(1))
                else:
                    print('Unmatched Net:',start)

    print(net)