from PyQt5.QtGui import QIntValidator
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
import os
import sys
from scipy import interpolate
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import QProcess
from src import read
import shutil
from datetime import datetime
from ._subwindow import processing, config


def pyqt5plot():
    app = QtWidgets.QApplication(sys.argv)
    main = plotGUI()
    main.show()
    app.exec_()


class plotGUI(QtWidgets.QMainWindow):
    def __init__(self,root):
        super().__init__()
        # self.Cir = Cir

        self.root=root
        os.chdir('./src')
        uic.loadUi('main.ui', self)
        os.chdir('../Workspace')
        self.setWindowTitle("Tolerance Analysis Tool")

        self.addToolBar(NavigationToolbar(self.MplWidget.canvas,self))

        self.dialog = processing()

        self.onlyInt = QIntValidator()
        self.addtimetext.setValidator(self.onlyInt)

        self.totaltime.setText('Total simulation time: 0')

        reg_ex = QtCore.QRegExp("[0-9]+\.*[0-9]*")
        self.calctext.setValidator(
            QtGui.QRegExpValidator(reg_ex, self.calctext))

        self.actionOpen_File.triggered.connect(self.openfile)

        self.p = None

    def openfile(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open file', '..', "Spice Netlists (*.cir)")
        if fname:
            name = fname.split('/')[-1]
            dir=name.split('.')[0]+' '+datetime.now().strftime("%d%m%Y_%H%M%S")
            os.mkdir(dir)
            os.chdir(dir)
            shutil.copyfile(fname, os.getcwd()+f'/{name}')

            self.Cir2 = read.circuit(fname)
            self.Cir2.shortname=name
            self.Cir2.dir=os.getcwd()

            message = self.Cir2.read()

            if message:
                QtWidgets.QMessageBox.critical(self, 'Error', message)
                return
            else:
                message, flag = self.Cir2.init()

                i = -1
                includefile = []
                while True:
                    i += 1
                    if flag:
                        ret = QtWidgets.QMessageBox.critical(
                            self, 'Error', message, QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Open)

                        if ret == QtWidgets.QMessageBox.Open:
                            temp, _ = QtWidgets.QFileDialog.getOpenFileName(
                                self, 'Select file for '+self.Cir2.subckt, '', "Model Files (*)")
                            includefile.append(
                                temp.split('/')[-1].split('.')[0])
                            if temp:
                                shutil.copyfile(
                                    temp, os.getcwd()+'/lib/user/'+includefile[i])
                                print('Copy '+temp+' to ' +
                                      os.getcwd()+'/lib/user/')
                                message, flag = self.Cir2.fixinclude(
                                    includefile[i], flag)
                        else:
                            for file in includefile:
                                read.rm('../lib/user/'+file)
                            return

                    elif message:
                        QtWidgets.QMessageBox.critical(self, 'Error', message)
                        for file in includefile:
                            read.rm('../lib/user/'+file)
                        return

                    else:
                        break

            self.configGUI=config(self.Cir2,self.root)
            self.configGUI.accepted.connect(lambda: self.configCreate(True))
            self.configGUI.rejected.connect(self.configreject)

        else:
            return

    def configCreate(self,i=False):
        if i:
            self.Cir=self.Cir2
        print('Config Entered')

        self.Cir.mc_runs=self.configGUI.totaltime.value()
        self.Cir.netselect=self.configGUI.measnode.currentText()
        self.Cir.analmode=self.configGUI.analmode.currentIndex()
        self.Cir.measmode=self.configGUI.measmode.currentText()
        self.Cir.rfnum=self.configGUI.rfnum.value()
        self.Cir.risefall=self.configGUI.risefall.currentIndex()

        if self.Cir.analmode==0:
            self.Cir.startac=self.configGUI.startac.value()*10**(self.configGUI.startunit.currentIndex()*3)
            self.Cir.stopac=self.configGUI.stopac.value()*10**(self.configGUI.stopunit.currentIndex()*3)

        for i in range(self.Cir.lengthc):
            self.Cir.alter_c[i].tol = self.configGUI.Ctol[i].value()
        for i in range(self.Cir.lengthr):
            self.Cir.alter_r[i].tol = self.configGUI.Rtol[i].value()
        self.Cir.create_sp()
        self.Cir.create_wst()
        self.start_process('Open', 2)

    def configreject(self):
        print('Rejected')
        if hasattr(self,'Cir'):
            os.chdir(self.Cir.dir)

    def start_process(self, finishmode, runmode=0):
        if self.p is None:  # No process running.
            self.p = QProcess()
            # self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.finished.connect(lambda: self.finishrun(finishmode))

            self.process = self.processGui()

            self.p.start("python3", ['../../src/runspice.py', f'-{runmode}'])

    def processGui(self):
        self.dialog.show()
        self.dialog.rejected.connect(self.kill)

    def kill(self):
        if self.p:
            self.p.terminate()
            print('killed')
            self.p = None

    def finishrun(self, mode):
        if self.p == None:
            print('Cancelled')
            return

        self.p = None
        self.dialog.close()

        with open('run.log') as file_object:
            file=file_object.read()
            if 'out of interval' in file:
                QtWidgets.QMessageBox.critical(self, 'Error!','Cutoff frequency out of interval')
                self.analButton.clicked.connect(self.analy)
                return

        if mode == 'Add':
            self.Cir.resultdata(True)
            self.total = self.total+self.Cir.mc_runs

        elif mode == 'Adjust':
            self.Cir.resultdata()
            self.total = self.Cir.mc_runs
            self.tolcolor()

        elif mode == 'Open':
            self.Cir.resultdata(worst=True)
            self.postinit()
            return

        self.x = self.Cir.cutoff
        self.y = self.Cir.p
        self.plot()
        self.totaltime.setText(f'Total simulation time: {self.total}')
        self.fit = interpolate.interp1d(self.x, self.y, kind='linear')
        self.calcp()

    def postinit(self):
        self.x = self.Cir.cutoff
        self.y = self.Cir.p
        self.fit = interpolate.interp1d(self.x, self.y, kind='linear')
        self.total = self.Cir.mc_runs
        self.totaltime.setText(f'Total simulation time: {self.total}')

        self.analButton.clicked.connect(self.analy)
        self.ResetButton.clicked.connect(self.reset)
        self.addtimetext.returnPressed.connect(self.AddTime)
        self.wstcase.toggled.connect(self.plotwst)
        self.calctext.returnPressed.connect(self.calcp)

        try:
            for i in reversed(range(self.scroll.count())):
                self.scroll.itemAt(i).widget().deleteLater()
        except:
            self.scroll = QtWidgets.QVBoxLayout(self.rightwidget)

        self.scrollc = QtWidgets.QScrollArea(self.rightwidget)
        self.scrollc.setMaximumSize(QtCore.QSize(180, 150))
        self.layoutWidgetc = QtWidgets.QWidget(self.scrollc)

        self.C = ['']*self.Cir.lengthc
        self.Ctol = ['']*self.Cir.lengthc
        self.gridLayoutc = QtWidgets.QGridLayout(self.layoutWidgetc)
        for i in range(self.Cir.lengthc):
            self.C[i] = QtWidgets.QLabel(self.Cir.alter_c[i].name, self.layoutWidgetc)
            self.Ctol[i] = QtWidgets.QLabel(f'{self.Cir.alter_c[i].tol:.4f}',self.layoutWidgetc)
            self.C[i].setAlignment(QtCore.Qt.AlignCenter)
            self.Ctol[i].setAlignment(QtCore.Qt.AlignCenter)
            self.gridLayoutc.addWidget(self.C[i],i+1,0)
            self.gridLayoutc.addWidget(self.Ctol[i],i+1,1)

        self.titleC = QtWidgets.QLabel('Capacitor', self.layoutWidgetc)
        self.titleCt = QtWidgets.QLabel('Tolerance', self.layoutWidgetc)
        self.gridLayoutc.addWidget(self.titleC,0,0)
        self.gridLayoutc.addWidget(self.titleCt,0,1)
        self.scrollc.setWidget(self.layoutWidgetc)
        self.scrollc.setAlignment(QtCore.Qt.AlignHCenter)
        self.scroll.addWidget(self.scrollc)

        self.scrollr = QtWidgets.QScrollArea(self.rightwidget)
        self.scrollr.setMaximumSize(QtCore.QSize(180, 150))
        self.layoutWidgetr = QtWidgets.QWidget(self.scrollr)

        self.R = ['']*self.Cir.lengthr
        self.Rtol = ['']*self.Cir.lengthr
        self.gridLayoutr = QtWidgets.QGridLayout(self.layoutWidgetr)
        for i in range(self.Cir.lengthr):
            self.R[i] = QtWidgets.QLabel(self.Cir.alter_r[i].name, self.layoutWidgetr)
            self.Rtol[i] = QtWidgets.QLabel(f'{self.Cir.alter_r[i].tol:.4f}',self.layoutWidgetr)
            self.R[i].setAlignment(QtCore.Qt.AlignCenter)
            self.Rtol[i].setAlignment(QtCore.Qt.AlignCenter)
            self.gridLayoutr.addWidget(self.R[i],i+1,0)
            self.gridLayoutr.addWidget(self.Rtol[i],i+1,1)

        self.titleR = QtWidgets.QLabel('Resistor', self.layoutWidgetr)
        self.titleRt = QtWidgets.QLabel('Tolerance', self.layoutWidgetr)
        self.titleR.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayoutr.addWidget(self.titleR,0,0)
        self.gridLayoutr.addWidget(self.titleRt,0,1)
        self.scrollr.setWidget(self.layoutWidgetr)
        self.scrollr.setAlignment(QtCore.Qt.AlignHCenter)
        self.scroll.addWidget(self.scrollr)

        self.scroll.setAlignment(QtCore.Qt.AlignTop)
        self.plot()

    def plot(self):
        print('Plot')
        if self.x == []:
            return

        self . MplWidget .figure. clear()

        self.ax = self.MplWidget.figure.add_subplot(111)
        self.ax.set_ylim(-0.05, 1.05)
        self.line1 = self.ax . plot(self.x, self.y)
        # self .MplWidget . canvas . axes . legend (( 'cosinus' ,  'sinus' ), loc = 'upper right' )
        self.ax. set_title(f"Tolerance Analysis of {self.Cir.shortname}")
        self.ax.grid()
        self.ax.set_xlabel('Cutoff Frequency/Hz')
        self.ax.set_ylabel('CDF')
        self.plotwst()

    def plotwst(self):
        print('wst')
        if self.x == []:
            return
        if self.wstcase.isChecked():
            self.line2 = self.ax.plot(
                self.x[self.Cir.wst_index], self.y[self.Cir.wst_index], 'xr')
            self.ax.legend([self.line2[0]], ['Worst Case'])
        else:
            self.ax.legend()
            try:
                line = self.line2.pop(0)
                line.remove()
            except IndexError:
                pass

        self.MplWidget.canvas.draw()





    def AddTime(self):

        self.Cir.mc_runs = int(self.addtimetext.text())
        print(f'Added:{self.Cir.mc_runs}\n')
        self.Cir.create_sp()

        self.start_process('Add')

    def adjusttol(self):
        for i in range(self.Cir.lengthc):
            self.Cir.alter_c[i].tol = self.Ctol[i].value()
        for i in range(self.Cir.lengthr):
            self.Cir.alter_r[i].tol = self.Rtol[i].value()

        self.Cir.adjust = True
        self.Cir.create_sp()
        self.Cir.create_wst()

        self.start_process('Adjust', 2)

    def tolcolor(self):
        for i in range(self.Cir.lengthc):
            if self.Ctol[i].value() != self.Cir.alter_c[i].tol:
                self.Ctol[i].setStyleSheet("color: red")
            else:
                self.Ctol[i].setStyleSheet("color: black")
        for i in range(self.Cir.lengthr):
            if self.Rtol[i].value() != self.Cir.alter_r[i].tol:
                self.Rtol[i].setStyleSheet("color: red")
            else:
                self.Rtol[i].setStyleSheet("color: black")

    def calcp(self):
        try:
            fc = float(self.calctext.text())
        except:
            return
        larsmll = self.psign.currentText()
        unit = self.fcunit.currentIndex()

        if self.x == []:
            return
        # elif unit == 'kHz':
        #     fc = fc*1000
        # elif unit == 'MHz':
        #     fc = fc*1000000
        # elif unit == 'GHz':
        #     fc = fc*1000000000
        else:
            fc=fc*10**(unit*3)

        if fc < self.x[0]:
            if larsmll == '<':
                self.presult.setText('Result:0')
                return
            else:
                self.presult.setText('Result:1')
                return
        elif fc > self.x[-1]:
            if larsmll == '<':
                self.presult.setText('Result:1')
                return
            else:
                self.presult.setText('Result:0')
                return
        elif larsmll == '>':
            result = 1-self.fit(fc)
        else:
            result = self.fit(fc)

        self.presult.setText(f'Result:{np.round(result,4)}')


    def analy(self):
        self.configGUI=config(self.Cir,self.root)
        self.configGUI.startac.setValue(self.Cir.startac)
        self.configGUI.stopac.setValue(self.Cir.stopac)
        self.configGUI.accepted.connect(self.configCreate)


    def reset(self):
        print('Reset')
        self.ax.legend()
        try:
            line = self.line1.pop(0)
            line.remove()
        except IndexError:
            pass
        try:
            line = self.line2.pop(0)
            line.remove()
        except IndexError:
            pass

        # for i in range(self.Cir.lengthc):
        #     self.Ctol[i].setValue(self.Cir.tolc)
        #     self.Ctol[i].setStyleSheet("color: black")
        # for i in range(self.Cir.lengthr):
        #     self.Rtol[i].setValue(self.Cir.tolr)
        #     self.Rtol[i].setStyleSheet("color: black")

        self . MplWidget . canvas . draw()
        self.addtimetext.clear()
        self.total = 0
        self.totaltime.setText('Total simulation time: 0')
        self.x, self.y, self.Cir._col2 = [], [], []
        self.calctext.setPlaceholderText('0')
        self.presult.setText('Result: 1')