import read,write,plot
import os,sys

# filename=read.getfile()
filename='LPF.cir'
read.ReadCir(filename)
startac,stopac,alter_c,alter_r=read.init()
write.create_sp(startac,stopac,alter_c,alter_r)
write.ngspice()
print(f'{len(alter_c)} capacitance(s) and {len(alter_r)} resistance(s)')
app=plot.QtWidgets.QApplication(sys.argv)
main=plot.Window()
main.show()
app.exec_()