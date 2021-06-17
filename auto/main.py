import read,plot
import os,sys
from read import circuit

# filename=read.getfile()
filename='LPF.cir'
Cir=circuit(filename)
Cir.read()
Cir.init()
Cir.create_sp()
Cir.ngspice()
Cir.resultdata()

print(f'{len(Cir.alter_c)} capacitance(s) and {len(Cir.alter_r)} resistance(s)')
Cir.plotcdf()
# app=plot.QtWidgets.QApplication(sys.argv)
# main=plot.Window()
# main.show()
# app.exec_()