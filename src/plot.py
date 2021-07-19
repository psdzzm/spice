from .Logging import logger
import subprocess
from PyQt5.QtGui import QIntValidator
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
import os
import sys
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import QProcess
from . import read
import shutil
from datetime import datetime
from timeit import default_timer as timer
from ._subwindow import processing, config, reconnect
from quantiphy import Quantity
import psutil


def pyqt5plot():
    app = QtWidgets.QApplication(sys.argv)
    main = plotGUI()
    main.show()
    app.exec_()


class plotGUI(QtWidgets.QMainWindow):
    def __init__(self, root):
        super().__init__()

        self.root = root
        os.chdir('./src')
        uic.loadUi('main.ui', self)
        os.chdir('../Workspace')
        self.setWindowTitle("Tolerance Analysis Tool")

        self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))
        self.scroll = QtWidgets.QVBoxLayout(self.rightwidget)
        self.scroll.setAlignment(QtCore.Qt.AlignTop)

        self.dialog = processing()
        self.dialog.rejected.connect(self.kill)
        self.configGUI = config(self.root)
        self.configGUI.accepted.connect(self.configCreate)
        self.configGUI.rejected.connect(self.configreject)

        self.onlyInt = QIntValidator()
        self.addtimetext.setValidator(self.onlyInt)

        self.totaltime.setText('Total simulation time: 0')

        doubleval = QtGui.QDoubleValidator()
        doubleval.setBottom(0)
        self.calctext.setValidator(doubleval)

        self.actionOpen_File.triggered.connect(self.openfile)

        self.p = None

    def openfile(self):

        if hasattr(self, 'Cir'):
            ret = QtWidgets.QMessageBox.warning(self, 'Warning', 'You will lose currenct analysis result', QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok)
            if ret == QtWidgets.QMessageBox.Cancel:
                return
            else:
                del self.Cir
        try:
            for i in reversed(range(self.scroll.count())):
                self.scroll.itemAt(i).widget().deleteLater()
        except AttributeError:
            pass
        self.MplWidget.figure.clear()
        self.MplWidget.canvas.draw()
        reconnect(self.analButton.clicked)
        reconnect(self.ResetButton.clicked)
        reconnect(self.addtimetext.returnPressed)
        reconnect(self.wstcase.toggled)
        reconnect(self.calctext.returnPressed)

        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', self.root + '/CirFile', "Spice Netlists (*.cir *.net)")
        if fname:
            name = os.path.basename(fname)
            if os.path.abspath(fname + '/../../') != self.root + '/Workspace':
                dir = name.split('.')[0] + ' ' + datetime.now().strftime("%d%m%Y_%H%M%S")
                os.mkdir(self.root + '/Workspace/' + dir)
                os.chdir(self.root + '/Workspace/' + dir)
                shutil.copyfile(fname, os.getcwd() + f'/{name}')
                logger.info('Copy ' + fname + ' to ' + os.getcwd() + f'/{name}')
            else:
                os.chdir(os.path.dirname(fname))
                files = os.listdir()
                files.remove(name)
                for item in files:
                    os.remove(item)

            self.Cir = read.circuit(fname)
            self.Cir.shortname = name
            self.Cir.dir = os.getcwd()

            message = self.Cir.read()

            if message:
                QtWidgets.QMessageBox.critical(self, 'Error', message)
                return
            else:
                message, flag = self.Cir.init()

                i = -1
                includefile = []
                while True:
                    i += 1
                    if flag:
                        if i < self.Cir.includetime:
                            ret = QtWidgets.QMessageBox.critical(self, 'Error', message, QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Open)

                            if ret == QtWidgets.QMessageBox.Open:
                                temp, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Select file for ' + self.Cir.subckt, '', "Model Files (*)")
                                includefile.append(temp.split('/')[-1].split('.')[0])
                                if temp:
                                    shutil.copyfile(temp, self.root + '/Workspace/lib/user/' + includefile[i])
                                    logger.info('Copy ' + temp + ' to ' + self.root + '/Workspace/lib/user/' + includefile[i])
                                    message, flag = self.Cir.fixinclude(includefile[i], flag)
                            else:
                                logger.warning('Exit. Deleting the uploaded include file')
                                for file in includefile:
                                    read.rm('../lib/user/' + file)
                                return
                        else:
                            logger.error('Incorrect include file provided! Reset the input circuit')
                            for file in includefile:
                                read.rm('../lib/user/' + file)
                            with open('test.cir', 'w') as f1, open('run.cir', 'w') as f2:
                                f1.write(self.Cir.testtext)
                                f2.write(self.Cir.runtext)
                            message, flag = self.Cir.init()
                            message = 'Please provide the correct file for the include file\n' + message
                            i = -1
                            includefile = []

                    elif message:
                        QtWidgets.QMessageBox.critical(self, 'Error', message)
                        for file in includefile:
                            read.rm('../lib/user/' + file)
                        return

                    else:
                        break

            self.configGUI.init(self.Cir)
            reconnect(self.configGUI.rejected, self.configreject)
            self.configGUI.show()

        else:
            return

    def configCreate(self):
        def pre_run():
            self.Cir.create_prerun()
            subprocess.run('ngspice -b run_control_pre.sp -o run_log', shell=True, stdout=subprocess.DEVNULL)

            with open('run.log', 'a') as file_object, open('run_log') as b:
                file = b.read()
                file_object.write(file)
                read.rm('run_log')

            if 'out of interval' in file:
                QtWidgets.QMessageBox.critical(self, 'Error!', 'Cutoff frequency out of interval')
                logger.error('Cutoff frequency out of interval')
                self.Cir.total = 0
                reconnect(self.analButton.clicked, self.analy)
                return -1
            else:
                return 0

        logger.info('Config Entered')

        self.Cir.netselect = self.configGUI.measnode.currentText()
        self.Cir.compselect = self.configGUI.stepcomp.currentText()
        self.Cir.mc_runs = self.configGUI.totaltime.value()
        self.Cir.analmode = self.configGUI.analmode.currentIndex()
        self.Cir.measmode = self.configGUI.measmode.currentText()
        self.Cir.rfnum = self.configGUI.rfnum.value()
        self.Cir.risefall = self.configGUI.risefall.currentIndex()

        self.Cir.startac = self.configGUI.startac.value() * 10**(self.configGUI.startunit.currentIndex() * 3)
        self.Cir.stopac = self.configGUI.stopac.value() * 10**(self.configGUI.stopunit.currentIndex() * 3)
        if self.Cir.startac >= self.Cir.stopac:
            QtWidgets.QMessageBox.critical(self, 'Error!', 'Start point is larger than stop point')
            reconnect(self.analButton.clicked, self.analy)
            self.Cir.total = 0
            return

        if self.Cir.analmode == 1:
            if self.configGUI.stepcomp.currentIndex() < self.Cir.lengthc:
                self.__unit = 'F'
                startcomp = self.configGUI.startac_2.value() * 10**(self.configGUI.startunit_2.currentIndex() * 3 - 12)
                stopcomp = self.configGUI.stopac_2.value() * 10**(self.configGUI.stopunit_2.currentIndex() * 3 - 12)
                increcomp = self.configGUI.stopac_3.value() * 10**(self.configGUI.increunit_2.currentIndex() * 3 - 12)
            else:
                self.__unit = 'Ω'
                startcomp = self.configGUI.startac_2.value() * 10**(self.configGUI.startunit_2.currentIndex() * 3 - 3)
                stopcomp = self.configGUI.stopac_2.value() * 10**(self.configGUI.stopunit_2.currentIndex() * 3 - 3)
                increcomp = self.configGUI.stopac_3.value() * 10**(self.configGUI.increunit_2.currentIndex() * 3 - 3)

            if self.configGUI.analmode_2.currentIndex() == 0:
                if len(np.arange(startcomp, stopcomp, increcomp)) < 2:
                    QtWidgets.QMessageBox.critical(self, 'Error!', 'Start point is larger than stop point or step value is too large')
                    reconnect(self.analButton.clicked, self.analy)
                    self.Cir.total = 0
                    return

                self.Cir.stepValue = f'start={startcomp} stop={stopcomp} step={increcomp}'
                stepinfo = Quantity.extract(self.Cir.stepValue.replace(' ', '\n'), units=self.__unit)
                self._stepinfo = ''
                for p, q in stepinfo.items():
                    self._stepinfo += f'{p} = {q}\n'

            else:
                self.Cir.stepValue = f"values {' '.join(self.configGUI.plainTextEdit.toPlainText().split())}"
                self._stepinfo = self.Cir.stepValue

            if pre_run() == -1:
                return

            self.psign.clear()
            self.psign.addItem('=')
            self.fcunit.clear()
            if self.__unit == 'F':
                self.fcunit.addItems(['pF', 'nF', 'μF', 'mF', 'F'])
            else:
                self.fcunit.addItems(['mΩ', 'Ω', 'kΩ', 'MΩ'])

            self.Cir.create_step()
            self.start_process('Step')  # Runmode 0, only run control.sp
            return

        else:
            self.psign.clear()
            self.psign.addItems(['>', '<'])
            self.fcunit.clear()
            if self.Cir.measmode == 'Gain Ripple':
                self.fcunit.addItem('dB')
            else:
                self.fcunit.addItems(['Hz', 'kHz', 'MHz', 'GHz'])

            for i in range(self.Cir.lengthc):
                self.Cir.alter_c[i].tol = self.configGUI.Ctol[i].value()
            for i in range(self.Cir.lengthr):
                self.Cir.alter_r[i].tol = self.configGUI.Rtol[i].value()

            if pre_run() == -1:
                return

            self.Cir.create_sp()
            self.Cir.create_wst()

            self.start_process('Open', 1)

    def configreject(self):
        logger.warning('Configuration Rejected')
        os.chdir('..')
        reconnect(self.analButton.clicked, None, None)
        shutil.rmtree(self.Cir.dir)
        logger.warning('Delete ' + self.Cir.dir)
        logger.warning(os.getcwd())
        del self.Cir

    def start_process(self, finishmode, runmode=0):
        if self.p is None:  # No process running.
            self.p = QProcess()
            # self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.finished.connect(lambda: self.finishrun(finishmode))

            self.process = self.processGui()

            self._start = timer()
            logger.info('Spice Started')
            if runmode == 0:
                self.p.start("/bin/bash", ['-c', 'ngspice -b run_control.sp -o run_log'])
            elif runmode == 1:
                read.rm('fc', 'fc_wst', 'paramlist', 'paramwstlist')
                self.p.start("/bin/bash", ['-c', 'ngspice -b run_control.sp run_control_wst.sp -o run_log'])

    def processGui(self):
        self.dialog.show()

    def kill(self):
        if self.p:
            self.p.kill()
            self.p = None
            read.rm('run_log')
            logger.warning('Delete run_log')

    def finishrun(self, mode):
        logger.info(f'Spice time: {timer()-self._start}s')
        if self.p == None:
            logger.warning('Spice Killed')
            return
        else:
            logger.info('Spice Finished')

        self.p = None

        with open('run.log', 'a') as file_object, open('run_log') as b:
            file = b.read()
            file_object.write(file)
            read.rm('run_log')
            error_r = []
            for line in file.splitlines():
                if line.lower().lstrip().startswith('error'):
                    error_r.append(line)

        if error_r:
            self.dialog.close()
            if 'out of interval' in file:
                QtWidgets.QMessageBox.critical(self, 'Error!', 'Cutoff frequency out of interval')
                logger.error('Cutoff frequency out of interval')
            else:
                error_r = ''.join(error_r)
                QtWidgets.QMessageBox.critical(self, 'Error!', error_r)
                logger.error(error_r)
            self.Cir.total = 0
            reconnect(self.analButton.clicked, self.analy)
            return
        elif mode == 'Add':
            self.Cir.total = self.Cir.total + self.Cir.mc_runs
            self.Cir.resultdata(add=True)
        elif mode == 'Open':
            self.Cir.total = self.Cir.mc_runs
            self.Cir.resultdata(worst=True)
            self.postinit()
            self.dialog.close()
            return
        elif mode == 'Step':
            self.Cir.total = 0
            self.Cir.resultdata(mode='Step')
            self.postinit('Step')
            self.dialog.close()
            return

        self.dialog.close()
        self.x = self.Cir.cutoff
        self.y = self.Cir.p
        self.plot()
        self.totaltime.setText(f'Total simulation time: {self.Cir.total}')
        self.calcp()

    def postinit(self, mode=None):
        self.x = self.Cir.cutoff
        self.y = self.Cir.p
        self.totaltime.setText(f'Total simulation time: {self.Cir.total}')

        for i in reversed(range(self.scroll.count())):
            self.scroll.itemAt(i).widget().deleteLater()

        reconnect(self.analButton.clicked, self.analy)
        reconnect(self.ResetButton.clicked, self.reset)
        reconnect(self.calctext.returnPressed, self.calcp)

        if mode == 'Step':
            self.plot('Step')
            self.stepinfo = QtWidgets.QPlainTextEdit(self._stepinfo)
            self.stepinfo.setReadOnly(True)
            self.stepinfo.setMaximumSize(QtCore.QSize(180, 150))
            self.scroll.addWidget(self.stepinfo)
            return

        reconnect(self.addtimetext.returnPressed, self.AddTime)
        reconnect(self.wstcase.toggled, self.plotwst)

        self.scrollc = QtWidgets.QScrollArea(self.rightwidget)
        self.scrollc.setMaximumSize(QtCore.QSize(180, 150))
        self.layoutWidgetc = QtWidgets.QWidget(self.scrollc)

        self.C = [''] * self.Cir.lengthc
        self.Ctol = [''] * self.Cir.lengthc
        self.gridLayoutc = QtWidgets.QGridLayout(self.layoutWidgetc)
        for i in range(self.Cir.lengthc):
            self.C[i] = QtWidgets.QLabel(self.Cir.alter_c[i].name, self.layoutWidgetc)
            self.Ctol[i] = QtWidgets.QLabel(f'{self.Cir.alter_c[i].tol:.4f}', self.layoutWidgetc)
            self.C[i].setAlignment(QtCore.Qt.AlignCenter)
            self.Ctol[i].setAlignment(QtCore.Qt.AlignCenter)
            self.gridLayoutc.addWidget(self.C[i], i + 1, 0)
            self.gridLayoutc.addWidget(self.Ctol[i], i + 1, 1)

        self.titleC = QtWidgets.QLabel('Capacitor', self.layoutWidgetc)
        self.titleCt = QtWidgets.QLabel('Tolerance', self.layoutWidgetc)
        self.gridLayoutc.addWidget(self.titleC, 0, 0)
        self.gridLayoutc.addWidget(self.titleCt, 0, 1)
        self.scrollc.setWidget(self.layoutWidgetc)
        self.scrollc.setAlignment(QtCore.Qt.AlignHCenter)
        self.scroll.addWidget(self.scrollc)

        self.scrollr = QtWidgets.QScrollArea(self.rightwidget)
        self.scrollr.setMaximumSize(QtCore.QSize(180, 150))
        self.layoutWidgetr = QtWidgets.QWidget(self.scrollr)

        self.R = [''] * self.Cir.lengthr
        self.Rtol = [''] * self.Cir.lengthr
        self.gridLayoutr = QtWidgets.QGridLayout(self.layoutWidgetr)
        for i in range(self.Cir.lengthr):
            self.R[i] = QtWidgets.QLabel(self.Cir.alter_r[i].name, self.layoutWidgetr)
            self.Rtol[i] = QtWidgets.QLabel(f'{self.Cir.alter_r[i].tol:.4f}', self.layoutWidgetr)
            self.R[i].setAlignment(QtCore.Qt.AlignCenter)
            self.Rtol[i].setAlignment(QtCore.Qt.AlignCenter)
            self.gridLayoutr.addWidget(self.R[i], i + 1, 0)
            self.gridLayoutr.addWidget(self.Rtol[i], i + 1, 1)

        self.titleR = QtWidgets.QLabel('Resistor', self.layoutWidgetr)
        self.titleRt = QtWidgets.QLabel('Tolerance', self.layoutWidgetr)
        self.titleR.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayoutr.addWidget(self.titleR, 0, 0)
        self.gridLayoutr.addWidget(self.titleRt, 0, 1)
        self.scrollr.setWidget(self.layoutWidgetr)
        self.scrollr.setAlignment(QtCore.Qt.AlignHCenter)
        self.scroll.addWidget(self.scrollr)

        self.plot()

    def plot(self, mode=None):
        logger.info('Plot')
        if self.x == []:
            logger.warning('Nothing to plot')
            return

        self.MplWidget.figure.clear()
        self.ax = self.MplWidget.figure.add_subplot(111)
        # self.ax.set_ylim(-0.05, 1.05)
        # t = int(self.Cir.cutoff[-1] - self.Cir.cutoff[0])
        # x = np.linspace(self.Cir.cutoff[0], self.Cir.cutoff[-1], 10**4 if t < 10**3 else 10**6 if t > 10**5 else 10 * t)
        # self.ax.plot(x,self.Cir.fit(x))
        self.line1 = self.ax.plot(self.x, self.y)
        self.ax. set_title(f"Tolerance Analysis of {self.Cir.shortname}")
        self.ax.grid()

        if mode == 'Step':
            if len(self.x) < 25:
                line = self.line1.pop(0)
                line.remove()
                self.line1 = self.ax.plot(self.x, self.y, marker='x')

            self.ax.set_xlabel(f'{self.Cir.compselect}/{self.__unit}')
            if self.Cir.measmode == 'Cutoff Frequency':
                self.ax.set_ylabel('Cutoff Frequency/Hz')
            elif self.Cir.measmode == 'Gain Ripple':
                self.ax.set_ylabel('Gain Ripple/dB')
            else:
                self.ax.set_ylabel('Gain/dB')
            self.MplWidget.canvas.draw()
        else:
            if self.Cir.measmode == 'Cutoff Frequency':
                self.ax.set_xlabel('Cutoff Frequency/Hz')
            elif self.Cir.measmode == 'Gain Ripple':
                self.ax.set_xlabel('Gain Ripple/dB')
            else:
                self.ax.set_xlabel('Gain/dB')
            self.ax.set_ylabel('CDF')
            self.plotwst(True)

    def plotwst(self, mode=None):
        logger.info('wst')
        if self.x == [] or mode == None:
            return

        self.ax.legend()
        try:
            line = self.line2.pop(0)
            line.remove()
        except:
            pass

        if self.wstcase.isChecked():
            self.line2 = self.ax.plot([self.Cir.wst_cutoff[0], self.Cir.wst_cutoff[-1]], [0, 1], 'xr')
            self.ax.legend([self.line2[0]], ['Worst Case'])

        self.MplWidget.canvas.draw()

    def AddTime(self):
        self.Cir.mc_runs = int(self.addtimetext.text())
        logger.info(f'Added:{self.Cir.mc_runs}')
        self.Cir.create_sp(add=True)

        self.start_process('Add')

    def calcp(self):
        try:
            fc = float(self.calctext.text())
        except SyntaxError:
            self.presult.setText('Result: SyntaxError')
            return
        larsmll = self.psign.currentText()
        unit = self.fcunit.currentIndex()

        if self.x == []:
            return
        else:
            if 'Hz' in self.fcunit.currentText():
                fc = fc * 10**(unit * 3)
            elif 'F' in self.fcunit.currentText():
                fc = fc * 10**(unit * 3 - 12)
            elif 'Ω' in self.fcunit.currentText():  # dB no need to change
                fc = fc * 10**(unit * 3 - 3)

        if self.Cir.analmode == 1:
            if fc < self.x[0] or fc > self.x[-1]:
                self.presult.setText('Result: Invalid')
                return
            else:
                result = self.Cir.fit(fc)

        else:
            if fc < self.x[0]:
                if larsmll == '<':
                    self.presult.setText('Result: 0')
                else:
                    self.presult.setText('Result: 1')
                return
            elif fc > self.x[-1]:
                if larsmll == '<':
                    self.presult.setText('Result: 1')
                else:
                    self.presult.setText('Result: 0')
                return
            elif larsmll == '>':
                result = self.y[-1] - self.Cir.fit(fc)
            else:
                result = self.Cir.fit(fc)

        self.presult.setText(f'Result:{np.round(result,4)}')

    def analy(self):
        self.configGUI.show()
        reconnect(self.configGUI.rejected, None, None)

    def reset(self):
        logger.info('Reset')
        self.ax.legend()
        try:
            line = self.line1.pop(0)
            line.remove()
        except IndexError:
            pass
        try:
            line = self.line2.pop(0)
            line.remove()
        except (IndexError, AttributeError):
            pass

        self.MplWidget.canvas.draw()
        self.addtimetext.clear()
        self.Cir.total = 0
        self.totaltime.setText('Total simulation time: 0')
        self.x, self.y, self.Cir._col2 = [], [], []
        self.calctext.setPlaceholderText('0')
        self.presult.setText('Result: 1')
