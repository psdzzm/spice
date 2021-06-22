from PyQt5.QtGui import QIntValidator, QMovie
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
import os
import sys
from scipy import interpolate
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal,QProcess
from src import read
import shutil


def plotcdf():
    with open('fc', "r") as fileobject:
        lines = fileobject.readlines()
    file1 = []
    row = []
    for line in lines:
        row = line.split()
        file1.append(row)

    # col1=[]
    col2 = []
    for row0 in file1:
        # col1.append(row0[0])
        col2.append(row0[1])

    # del col1[0]
    del col2[0]

    length = len(col2)
    # cout=np.zeros(length)
    cutoff = np.zeros(length)

    for i in range(length):
        # cout[i]=float(col1[i])
        cutoff[i] = float(col2[i])

    # index=cutoff.argsort()
    cutoff = list(set(cutoff))
    length = len(cutoff)
    cutoff.sort()

    xaxis = np.linspace(cutoff[0], cutoff[-1], length)
    yaxis = np.arange(1, 1+length)/length
    return cutoff, yaxis

    smooth = interpolate.interp1d(cutoff, yaxis, kind='cubic')

    # fig=plt.figure()
    # ax=plt.gca()

    plt.title("Cdf of Cutoff Frequency")
    plt.xlabel("Cutoff Frequency/Hz")
    plt.ylabel("Cdf")
    plt.grid()
    plt.plot(cutoff, smooth(cutoff), 'b', cutoff, yaxis+0.1, 'r')
    plt.show()


def pyqt5plot():
    app = QtWidgets.QApplication(sys.argv)
    main = plotGUI()
    main.show()
    # gui=plotGUI()
    # gui.ui.show()
    app.exec_()


class plotGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # self.Cir = Cir

        os.chdir('./src')
        uic.loadUi('main.ui', self)
        os.chdir('../Workspace')
        self.setWindowTitle("Tolerance Analysis Tool")


        self . addToolBar(NavigationToolbar(self . MplWidget . canvas,  self))

        self.onlyInt = QIntValidator()
        self.addtimetext.setValidator(self.onlyInt)

        self.totaltime.setText(
            f'Total simulation time: 0')


        reg_ex = QtCore.QRegExp("[0-9]+\.*[0-9]*")
        self.calctext.setValidator(
            QtGui.QRegExpValidator(reg_ex, self.calctext))

        self.actionOpen_File.triggered.connect(self.openfile)

        self.p=None


    def AddTime(self):

        self.Cir.mc_runs = int(self.addtimetext.text())
        print(f'Added:{self.Cir.mc_runs}\n')
        self.Cir.create_sp()

        self.start_process('Add')



    def adjusttol(self):
        for i in range(self.Cir.lengthc):
            self.Cir.alter_c[i].tol=self.Ctol[i].value()
        for i in range(self.Cir.lengthr):
            self.Cir.alter_r[i].tol=self.Rtol[i].value()

        self.Cir.adjust=True
        self.Cir.create_sp()
        self.Cir.create_wst()

        self.start_process('Adjust',2)


    def tolcolor(self):
        for i in range(self.Cir.lengthc):
            if self.Ctol[i].value()!=self.Cir.alter_c[i].tol:
                self.Ctol[i].setStyleSheet("color: red")
            else:
                self.Ctol[i].setStyleSheet("color: black")
        for i in range(self.Cir.lengthr):
            if self.Rtol[i].value()!=self.Cir.alter_r[i].tol:
                self.Rtol[i].setStyleSheet("color: red")
            else:
                self.Rtol[i].setStyleSheet("color: black")

    def calcp(self):
        try:
            fc = float(self.calctext.text())
        except:
            return
        larsmll = self.psign.currentText()
        unit = self.fcunit.currentText()

        if self.x ==[]:
            return
        elif unit == 'kHz':
            fc = fc*1000
        elif unit == 'MHz':
            fc = fc*1000000
        elif unit == 'GHz':
            fc = fc*1000000000

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

        print(result)
        self.presult.setText(f'Result:{np.round(result,4)}')

    def postinit(self):
        self.x = self.Cir.cutoff
        self.y = self.Cir.p
        self.fit = interpolate.interp1d(self.x, self.y, kind='linear')
        self.total = self.Cir.mc_runs
        self.totaltime.setText(f'Total simulation time: {self.total}')

        self.analButton.clicked.connect(self.plot)
        self.ResetButton.clicked.connect(self.reset)
        self.addtimetext.returnPressed.connect(self.AddTime)
        self.wstcase.toggled.connect(self.plotwst)
        self.calctext.returnPressed.connect(self.calcp)

        try:
            for i in reversed(range(self.scroll.count())):
                print(i)
                self.scroll.itemAt(i).widget().deleteLater()
        except:
            self.scroll = QtWidgets.QVBoxLayout(self.rightwidget)


        self.scrollc = QtWidgets.QScrollArea(self.rightwidget)
        self.scrollc.setMaximumSize(QtCore.QSize(180, 150))
        self.layoutWidgetc = QtWidgets.QWidget(self.scrollc)

        self.C = ['']*self.Cir.lengthc
        self.Ctol = ['']*self.Cir.lengthc
        self.formLayoutc = QtWidgets.QFormLayout(self.layoutWidgetc)
        for i in range(self.Cir.lengthc):
            self.C[i] = QtWidgets.QLabel(f'{self.Cir.alter_c[i].name}', self.layoutWidgetc)
            self.Ctol[i] = QtWidgets.QDoubleSpinBox(self.layoutWidgetc)
            self.Ctol[i].setValue(self.Cir.alter_c[i].tol)
            self.Ctol[i].valueChanged.connect(self.tolcolor)
            self.Ctol[i].setSingleStep(0.01)
            self.Ctol[i].setMaximum(0.9999)
            self.Ctol[i].setDecimals(4)
            self.Ctol[i].setMaximumWidth(85)
            self.formLayoutc.setWidget(
                i+1, QtWidgets.QFormLayout.LabelRole, self.C[i])
            self.formLayoutc.setWidget(
                i+1, QtWidgets.QFormLayout.FieldRole, self.Ctol[i])

        self.titleC = QtWidgets.QLabel('Capacitor', self.layoutWidgetc)
        self.titleC.setAlignment(QtCore.Qt.AlignCenter)
        self.formLayoutc.setWidget(
            0, QtWidgets.QFormLayout.SpanningRole, self.titleC)
        self.scrollc.setWidget(self.layoutWidgetc)
        self.scroll.addWidget(self.scrollc)

        self.scrollr = QtWidgets.QScrollArea(self.rightwidget)
        self.scrollr.setMaximumSize(QtCore.QSize(16777215, 150))
        self.layoutWidgetr = QtWidgets.QWidget(self.scrollr)

        # self.Cir.lengthr = 10
        self.R = ['']*self.Cir.lengthr
        self.Rtol = ['']*self.Cir.lengthr
        self.formLayoutr = QtWidgets.QFormLayout(self.layoutWidgetr)
        for i in range(self.Cir.lengthr):
            self.R[i] = QtWidgets.QLabel(f'{self.Cir.alter_r[i].name}', self.layoutWidgetr)
            self.Rtol[i] = QtWidgets.QDoubleSpinBox(self.layoutWidgetr)
            self.Rtol[i].setValue(self.Cir.alter_r[i].tol)
            self.Rtol[i].valueChanged.connect(self.tolcolor)
            self.Rtol[i].setSingleStep(0.01)
            self.Rtol[i].setMaximum(0.9999)
            self.Rtol[i].setDecimals(4)
            self.Rtol[i].setMaximumWidth(85)
            self.formLayoutr.setWidget(
                i+1, QtWidgets.QFormLayout.LabelRole, self.R[i])
            self.formLayoutr.setWidget(
                i+1, QtWidgets.QFormLayout.FieldRole, self.Rtol[i])
        self.titleR = QtWidgets.QLabel('Resistor', self.layoutWidgetr)
        self.titleR.setAlignment(QtCore.Qt.AlignCenter)
        self.formLayoutr.setWidget(
            0, QtWidgets.QFormLayout.SpanningRole, self.titleR)
        self.scrollr.setWidget(self.layoutWidgetr)
        self.scroll.addWidget(self.scrollr)

        self.pushSet = QtWidgets.QPushButton('Set', self.rightwidget)
        self.scroll.addWidget(self.pushSet)
        self.scroll.setAlignment(QtCore.Qt.AlignTop)

        self.pushSet.clicked.connect(self.adjusttol)

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
        self.ax. set_title(f"Tolerance Analysis of {self.Cir.name}")
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
            self.ax.legend([self.line2[0]],['Worst Case'])
        else:
            self.ax.legend()
            try:
                line = self.line2.pop(0)
                line.remove()
            except IndexError:
                pass

        self . MplWidget . canvas . draw()

    def openfile(self):
        fname,_ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file','../CirFile', "Spice Netlists (*.cir)")
        if fname:
            name=fname.split('/')[-1]
            print(os.getcwd())
            shutil.copyfile(fname,os.getcwd()+f'/{name}')
            self.Cir=read.circuit(name)

            message=self.Cir.read()
            if message:
                QtWidgets.QMessageBox.critical(self,'Error',message)
                return
            else:
                message,flag=self.Cir.init()
                if flag:
                    ret=QtWidgets.QMessageBox.critical(self,'Error',message,QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Open)
                    if ret==QtWidgets.QMessageBox.Open:
                        fname,_ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file','', "Spice Netlists (*.cir)")
                        if fname:
                            print(fname)
                    return
                elif message:
                    QtWidgets.QMessageBox.critical(self,'Error',message)
                    return

            self.Cir.mc_runs,ok=QtWidgets.QInputDialog().getInt(self,'Run Time','Run Time',100,1)
            if not ok:
                return

            self.Cir.create_sp()
            self.Cir.create_wst()

            self.start_process('Open',2)

        else:
            return

    def start_process(self,finishmode,runmode=0):
        if self.p is None:  # No process running.
            # self.message("Executing process")
            print(os.getcwd())
            self.p = QProcess()
            # self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.finished.connect(lambda: self.finishrun(finishmode))

            self.process=self.newGui()

            self.p.start("python3.9",['../src/runspice.py',f'-{runmode}'])

    def newGui(self):
        self.dialog = processing()
        self.dialog.rejected.connect(self.kill)
        self.dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        self.dialog.show()

    def kill(self):
        if self.p:
            self.p.terminate()
            print('killed')
            self.p=None

    def finishrun(self,mode):
        if self.p==None:
            print('Cancelled')
            return

        self.p=None
        self.dialog.close()
        if mode=='Add':
            self.Cir.resultdata(True)
            self.total = self.total+self.Cir.mc_runs

        elif mode=='Adjust':
            self.Cir.resultdata()
            self.total = self.Cir.mc_runs
            self.tolcolor()

        elif mode=='Open':
            self.Cir.resultdata(worst=True)
            self.postinit()
            return

        self.x = self.Cir.cutoff
        self.y = self.Cir.p
        self.plot()
        self.totaltime.setText(f'Total simulation time: {self.total}')
        self.fit = interpolate.interp1d(self.x, self.y, kind='linear')
        self.calcp()


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

        for i in range(self.Cir.lengthc):
            self.Ctol[i].setValue(self.Cir.tolc)
            self.Ctol[i].setStyleSheet("color: black")
        for i in range(self.Cir.lengthr):
            self.Rtol[i].setValue(self.Cir.tolr)
            self.Rtol[i].setStyleSheet("color: black")

        self . MplWidget . canvas . draw()
        self.addtimetext.clear()
        self.calctext.setPlaceholderText('0')
        self.total = 0
        self.totaltime.setText(f'Total simulation time: 0')
        self.x, self.y, self.Cir._col2 = [], [], []
        self.calctext.setPlaceholderText('0')
        self.presult.setText('Result: 1')





class processing(QtWidgets.QDialog):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        uic.loadUi('../src/processing.ui',self)
        self.setWindowTitle('Processing')