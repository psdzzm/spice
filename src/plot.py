# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description: GUI Interface
 Author: Yichen Zhang
 Date: 01-08-2021 20:16:10
 LastEditors: Yichen Zhang
 LastEditTime: 04-08-2021 16:37:46
 FilePath: /spice/src/plot.py
'''
import re
from .Logging import logger
import subprocess
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
import os
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import QProcess
from .read import circuit, rm
import shutil
from datetime import datetime
from timeit import default_timer as timer
from ._subwindow import processing, config, reconnect
from quantiphy import Quantity


# The top GUI calss
class plotGUI(QtWidgets.QMainWindow):
    def __init__(self, root):
        super().__init__()

        self.root = root    # Root directory
        os.chdir('./src')
        uic.loadUi('main.ui', self)  # Load ui file
        os.chdir('../Workspace')
        self.setWindowTitle("Tolerance Analysis Tool")

        # Add matplotlib tool bar
        self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))
        self.scroll = QtWidgets.QVBoxLayout(self.rightwidget)
        self.scroll.setAlignment(QtCore.Qt.AlignTop)

        self.dialog = processing()  # Initialize processing window
        self.dialog.rejected.connect(self.kill)     # Cancel clicked when analysing
        self.configGUI = config(self.root)  # Initialize configuration window
        self.configGUI.accepted.connect(self.configCreate)  # OK clicked in configuration
        self.configGUI.rejected.connect(self.configreject)  # Cancel clicked

        onlyInt = QtGui.QIntValidator()
        onlyInt.setBottom(1)
        self.addtimetext.setValidator(onlyInt)

        doubleval = QtGui.QDoubleValidator()
        doubleval.setBottom(0)
        self.calctext.setValidator(doubleval)

        self.actionOpen_File.triggered.connect(self.openfile)   # Open File clicked

        self.p = None   # Initialize the variable referred to ngspice process

    def openfile(self):

        if hasattr(self, 'Cir'):    # There is a file opened
            ret = QtWidgets.QMessageBox.warning(self, 'Warning', 'You will lose currenct analysis result', QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok)
            if ret == QtWidgets.QMessageBox.Cancel:
                return
            else:
                del self.Cir
        try:    # Delete all widgets in right panel
            for i in reversed(range(self.scroll.count())):
                self.scroll.itemAt(i).widget().deleteLater()
        except AttributeError:
            pass

        # Clear figure and disconnect signals
        self.MplWidget.figure.clear()
        self.MplWidget.canvas.draw()
        reconnect(self.analButton.clicked)
        reconnect(self.ResetButton.clicked)
        reconnect(self.addtimetext.returnPressed)
        reconnect(self.wstcase.toggled)
        reconnect(self.calctext.returnPressed)

        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', self.root + '/CirFile', "Spice Netlists (*.cir *.net)")
        if fname:   # Absolute path
            name = os.path.basename(fname)  # File name
            if os.path.abspath(fname + '/../../') != self.root + '/Workspace':
                # Create a folder to save uploaded file
                dir = name.split('.')[0] + ' ' + datetime.now().strftime("%d%m%Y_%H%M%S")
                os.mkdir(self.root + '/Workspace/' + dir)   # Make folder
                os.chdir(self.root + '/Workspace/' + dir)   # Change working folder
                shutil.copyfile(fname, os.getcwd() + f'/{name}')
                logger.info('Copy ' + fname + ' to ' + os.getcwd() + f'/{name}')
            else:
                # The uploaded file is in existing Workspace foler
                os.chdir(os.path.dirname(fname))
                files = os.listdir()
                files.remove(name)
                for item in files:      # Delete all other files
                    os.remove(item)

            self.Cir = circuit(fname)  # Instantiate circuit
            self.Cir.basename = name
            self.Cir.dir = os.getcwd()  # Record where it is

            message = self.Cir.read()   # Read circuit file

            if message:  # Fail to read
                QtWidgets.QMessageBox.critical(self, 'Error', message)
                return
            else:
                message, flag = self.Cir.init()  # Initialize circuit

                i = -1  # Count how many include files are needed
                includefile = []
                while True:
                    i += 1
                    if flag:    # Some error occur
                        if i < self.Cir.includetime:
                            ret = QtWidgets.QMessageBox.critical(self, 'Error', message, QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Open)

                            if ret == QtWidgets.QMessageBox.Open:   # 'Open' is clicked
                                # Get opened file full name
                                temp, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Select file for ' + self.Cir.subckt, '', "Model Files (*)")
                                if temp:
                                    # Get opened file base name
                                    includefile.append(os.path.basename(temp).split('.')[0])
                                    shutil.copyfile(temp, os.path.join(self.root, 'Workspace', 'lib', 'user', includefile[i]))
                                    logger.info('Copy ' + temp + ' to ' + self.root + '/Workspace/lib/user/' + includefile[i])
                                    message, flag = self.Cir.fixinclude(includefile[i], flag)
                                else:   # No file uploaded
                                    i -= 1    # Count file -1
                            else:
                                logger.warning('Exit. Deleting the uploaded include file')
                                for file in includefile:
                                    rm('../lib/user/' + file)
                                return

                        else:   # Incorrect include file is provided
                            logger.error('Incorrect include file provided! Reset the input circuit')
                            for file in includefile:
                                rm('../lib/user/' + file)  # Delete uploaded include files
                            # Rewrite test and run circuit
                            with open('test.cir', 'w') as f1, open('run.cir', 'w') as f2:
                                f1.write(self.Cir.testtext)
                                f2.write(self.Cir.runtext)
                            message, flag = self.Cir.init()
                            message = 'Please provide the correct file for the include file\n' + message
                            i = -1
                            includefile = []

                    elif message:   # Fatal error occur
                        QtWidgets.QMessageBox.critical(self, 'Error', message)
                        for file in includefile:
                            rm('../lib/user/' + file)
                        return

                    else:   # No error occur
                        break

            self.configGUI.init(self.Cir)   # Initialize configuration based on circuit
            reconnect(self.configGUI.rejected, self.configreject)
            self.configGUI.show()

        else:   # No file opened
            return

    # Ok is clicked in configuration window

    def configCreate(self):
        # Test circuit before formal simulation
        def pre_run():
            self.Cir.create_prerun()    # Create pre-run control file
            subprocess.run('ngspice -b run_control_pre.sp -o run_log', shell=True, stdout=subprocess.DEVNULL)

            with open('run.log', 'a') as file_object, open('run_log') as b:
                file = b.read()
                file_object.write(file)
                rm('run_log')

            error_r = []
            for line in file.splitlines():  # Detect if any error message in log file
                if line.lower().lstrip().startswith('error'):
                    error_r.append(line)

            if error_r:
                if 'out of interval' in file:
                    QtWidgets.QMessageBox.critical(self, 'Error!', 'Measured frequency out of interval')
                    logger.error('Measured frequency out of interval')
                else:
                    if sum(['\n' in s for s in error_r]) > 10:
                        error_r = ''.join(error_r[0:10]) + 'See run.log for more information'
                    else:
                        error_r = ''.join(error_r)
                    QtWidgets.QMessageBox.critical(self, 'Error!', error_r)
                    logger.error(error_r)

                # Do some initialize to the main window
                self.Cir.total = 0
                reconnect(self.analButton.clicked, self.analy)
                return -1
            else:
                return 0

        logger.info('Config Entered')

        # Read parameters from configuration window
        self.Cir.netselect = self.configGUI.measnode.currentText()
        self.Cir.compselect = self.configGUI.stepcomp.currentText()
        self.Cir.mc_runs = self.configGUI.totaltime.value()
        self.Cir.analmode = self.configGUI.analmode.currentIndex()
        self.Cir.measmode = self.configGUI.measmode.currentText()
        self.Cir.rfnum = self.configGUI.rfnum.value()
        self.Cir.risefall = self.configGUI.risefall.currentIndex()

        self.Cir.startac = self.configGUI.startac.value() * 10**(self.configGUI.startunit.currentIndex() * 3)
        self.Cir.stopac = self.configGUI.stopac.value() * 10**(self.configGUI.stopunit.currentIndex() * 3)

        self.Cir.tol = self.configGUI.accptol.value()
        self.Cir.yd = self.configGUI.yd.value()

        if self.configGUI.tabWidget.currentIndex() == 3:    # Op amp mode
            self.Cir.netselect = self.configGUI.measnode_2.currentText()
            self.Cir.opselect = self.configGUI.opamp.currentText()
            self.Cir.simmode = self.configGUI.simmode.currentIndex()
            self.Cir.opnum = self.configGUI.replace.currentIndex() + 1
            if not hasattr(self.Cir, 'opamp') or None in self.Cir.opamp[0:self.Cir.opnum]:
                QtWidgets.QMessageBox.critical(self, 'Error!', 'Blank Op amp input!')
                reconnect(self.analButton.clicked, self.analy)
                self.Cir.total = 0
                return

            if self.Cir.simmode:    # Ac analysis
                self.Cir.startac = self.configGUI.startac_5.value() * 10**(self.configGUI.startunit_5.currentIndex() * 3)
                self.Cir.stopac = self.configGUI.stopac_5.value() * 10**(self.configGUI.stopunit_5.currentIndex() * 3)
            else:   # transient analysis
                self.Cir.startac = self.configGUI.startac_5.value() * 10**(self.configGUI.startunit_5.currentIndex() * 3 - 9)
                self.Cir.stopac = self.configGUI.stopac_5.value() * 10**(self.configGUI.stopunit_5.currentIndex() * 3 - 9)
                self.Cir.tstep = 10**(self.configGUI.stopunit_5.currentIndex() * 3 - 11)

            if self.Cir.startac >= self.Cir.stopac:
                QtWidgets.QMessageBox.critical(self, 'Error!', 'Start point is larger than stop point')
                reconnect(self.analButton.clicked, self.analy)
                self.Cir.total = 0
                return

            self.Cir.create_opamp()
            self.start_process('Opamp')  # Runmode 0, only run control.sp

        elif self.configGUI.tabWidget.currentIndex() == 2:    # CMRR mode
            self.Cir.inputnode = self.configGUI.inputnode.currentText()
            self.Cir.netselect = self.configGUI.outputnode.currentText()
            self.Cir.mc_runs = self.configGUI.cmrrtime.value()
            self.Cir.tol = self.configGUI.acptcmrr.value()
            self.Cir.yd = self.configGUI.cmrryd.value()
            self.Cir.freqcmrr = self.configGUI.freqcmrr.value() * 10**(self.configGUI.cmrrunit.currentIndex() * 3)
            if self.Cir.inputnode == self.Cir.netselect:
                QtWidgets.QMessageBox.critical(self, 'Error!', 'Duplicate nets selected')
                reconnect(self.analButton.clicked, self.analy)
                self.Cir.total = 0
                return

            self.fcunit.clear()
            self.fcunit.addItem('dB')
            self.Cir.create_cmrr()
            self.start_process('CMRR', 1)  # Runmode 1, run also worst case

        elif self.Cir.startac >= self.Cir.stopac:
            QtWidgets.QMessageBox.critical(self, 'Error!', 'Start point is larger than stop point')
            reconnect(self.analButton.clicked, self.analy)
            self.Cir.total = 0
            return

        elif self.Cir.analmode == 1:  # Step mode
            # Step component is capacitor
            if self.configGUI.stepcomp.currentIndex() < self.Cir.lengthc:
                self.__unit = 'F'
                # Convert value to that with SI unit
                startcomp = self.configGUI.startac_2.value() * 10**(self.configGUI.startunit_2.currentIndex() * 3 - 12)
                stopcomp = self.configGUI.stopac_2.value() * 10**(self.configGUI.stopunit_2.currentIndex() * 3 - 12)
                increcomp = self.configGUI.stopac_3.value() * 10**(self.configGUI.increunit_2.currentIndex() * 3 - 12)
            else:   # Step component is resistor
                self.__unit = 'Ω'
                startcomp = self.configGUI.startac_2.value() * 10**(self.configGUI.startunit_2.currentIndex() * 3 - 3)
                stopcomp = self.configGUI.stopac_2.value() * 10**(self.configGUI.stopunit_2.currentIndex() * 3 - 3)
                increcomp = self.configGUI.stopac_3.value() * 10**(self.configGUI.increunit_2.currentIndex() * 3 - 3)

            # Step type is linear
            if self.configGUI.analmode_2.currentIndex() == 0:
                if len(np.arange(startcomp, stopcomp, increcomp)) < 2:  # Step points are too few
                    QtWidgets.QMessageBox.critical(self, 'Error!', 'Start point is larger than stop point or step value is too large')
                    reconnect(self.analButton.clicked, self.analy)
                    self.Cir.total = 0
                    return

                self.Cir.stepValue = f'start={startcomp} stop={stopcomp} step={increcomp}'
                # Below code is used to get texts to display step info on the main window
                stepinfo = Quantity.extract(self.Cir.stepValue.replace(' ', '\n'), units=self.__unit)
                self._stepinfo = ''
                for p, q in stepinfo.items():
                    self._stepinfo += f'{p} = {q}\n'

            # Step type is list
            else:
                text = self.configGUI.plainTextEdit.toPlainText()
                check = re.compile(r'[^\d\.\npnuμmkKMGT ]+').search(text)  # Chck if list has any invalid charaecter
                if check:
                    QtWidgets.QMessageBox.critical(self, 'Error!', f'Invalid Character {check.group()}')
                    reconnect(self.analButton.clicked, self.analy)
                    self.Cir.total = 0
                    return
                else:   # No invalid characters
                    self.Cir.stepValue = f"values {' '.join(text.split())}"
                    self._stepinfo = self.Cir.stepValue  # Text to show in main window

            if pre_run() == -1:  # Check before simualtion failed
                return

            # Clear and add items to combo box
            self.psign.clear()
            self.psign.addItem('=')
            self.fcunit.clear()
            if self.__unit == 'F':
                self.fcunit.addItems(['pF', 'nF', 'μF', 'mF', 'F'])
            else:
                self.fcunit.addItems(['mΩ', 'Ω', 'kΩ', 'MΩ'])

            self.Cir.create_step()
            self.start_process('Step')  # Runmode 0, only run control.sp

        else:   # Ac Analysis mode
            self.psign.clear()
            self.psign.addItems(['>', '<'])
            self.fcunit.clear()
            if self.Cir.measmode == 'Gain Ripple':
                self.fcunit.addItem('dB')
            else:
                self.fcunit.addItems(['Hz', 'kHz', 'MHz', 'GHz'])

            # Read in tolerance of each component
            for i in range(self.Cir.lengthc):
                self.Cir.alter_c[i].tol = self.configGUI.Ctol[i].value()
            for i in range(self.Cir.lengthr):
                self.Cir.alter_r[i].tol = self.configGUI.Rtol[i].value()

            if pre_run() == -1:
                return

            self.Cir.create_sp()
            self.Cir.create_wst()

            self.start_process('Open', 1)   # Runmode 1, with worst case analysis

    # Cancel is clicked in configuration window

    def configreject(self):
        logger.warning('Configuration Rejected')
        os.chdir('..')
        reconnect(self.analButton.clicked, None, None)  # Disconnect all signal of Analysis button
        shutil.rmtree(self.Cir.dir)  # Delete folder
        logger.warning('Delete ' + self.Cir.dir)
        logger.warning(os.getcwd())
        del self.Cir

    # Call ngspice to run simulation
    def start_process(self, finishmode, runmode=0):
        if self.p is None:  # No process running.
            self.p = QProcess()     # Create subprocess
            # self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.finished.connect(lambda: self.finishrun(finishmode))

            self.dialog.show()   # Show Processing window

            self._start = timer()
            logger.info('Spice Started')
            if runmode == 0:
                self.p.start("/bin/bash", ['-c', 'ngspice -b run_control.sp -o run_log'])
            elif runmode == 1:
                rm('fc', 'fc_wst', 'paramlist', 'paramwstlist')
                self.p.start("/bin/bash", ['-c', 'ngspice -b run_control.sp run_control_wst.sp -o run_log'])

    # Kill ngspice
    def kill(self):
        if self.p:
            self.p.kill()
            self.p = None
            rm('run_log')
            logger.warning('Delete run_log')
            reconnect(self.analButton.clicked, self.analy)

    # Ngspice finish run
    def finishrun(self, mode):
        if self.p == None:
            logger.warning('Spice Killed')
            return
        else:
            logger.info('Spice Finished')
            self.p = None

        with open('run.log', 'a') as file_object, open('run_log') as b:
            file = b.read()
            file_object.write(file)
            rm('run_log')
            error_r = []
            for line in file.splitlines(keepends=True):
                if line.lower().lstrip().startswith('error'):
                    error_r.append(line)

        logger.info(f'Spice time: {timer()-self._start}s')

        if error_r:
            self.dialog.close()
            if 'out of interval' in file:
                QtWidgets.QMessageBox.critical(self, 'Error!', 'Cutoff frequency out of interval')
                logger.error('Cutoff frequency out of interval')
            else:
                if sum(['\n' in s for s in error_r]) > 10:
                    error_r = ''.join(error_r[0:10]) + 'See run.log for more information'
                else:
                    error_r = ''.join(error_r)
                QtWidgets.QMessageBox.critical(self, 'Error!', error_r)
                logger.error(error_r)
            self.Cir.total = 0
            reconnect(self.analButton.clicked, self.analy)
            return
        elif 'Add' in mode:
            self.Cir.total = self.Cir.total + self.Cir.mc_runs
            self.Cir.resultdata(add=True)
            self.x = self.Cir.cutoff
            self.y = self.Cir.p
            self.plot(mode)
            self.totaltime.setText(f'Total simulation time: {self.Cir.total}')
            self.calcp()
        elif mode == 'Open' or mode == 'CMRR':
            self.Cir.total = self.Cir.mc_runs
            self.Cir.resultdata(worst=True)
            self.postinit(mode)     # Doing some initialize as it is the first run after file opened
        elif mode == 'Step':    # Mode is step, not ac analysis
            self.Cir.total = 0
            self.Cir.resultdata(mode='Step')
            self.postinit('Step')
        elif mode == 'Opamp':
            self.Cir.total = 0
            self.Cir.resultdata(mode='Opamp')
            self.postinit('Opamp')

        self.dialog.close()  # Close processing window

    # Doing some initialize
    def postinit(self, mode=None):
        self.x = self.Cir.cutoff
        self.y = self.Cir.p
        self.totaltime.setText(f'Total simulation time: {self.Cir.total}')

        # Delete all widgets in right side bar
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
            reconnect(self.addtimetext.returnPressed)
            reconnect(self.wstcase.toggled)
            return
        elif mode == 'Opamp':
            self.plot('Opamp')
            reconnect(self.addtimetext.returnPressed)
            reconnect(self.wstcase.toggled)
            reconnect(self.calctext.returnPressed)
            return

        # Below code is excuted if not step mode
        reconnect(self.addtimetext.returnPressed, self.AddTime)
        reconnect(self.wstcase.toggled, self.plotwst)

        self.scrollc = QtWidgets.QScrollArea(self.rightwidget)
        self.scrollc.setMaximumSize(QtCore.QSize(180, 150))
        self.layoutWidgetc = QtWidgets.QWidget(self.scrollc)

        # Below code adds component tolerance info to right side bar
        self.C = [''] * self.Cir.lengthc        # Label to display capacitance name
        self.Ctol = [''] * self.Cir.lengthc     # Label to display capacitance tolerance
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

        # Resistor
        self.scrollr = QtWidgets.QScrollArea(self.rightwidget)
        self.scrollr.setMaximumSize(QtCore.QSize(180, 150))
        self.layoutWidgetr = QtWidgets.QWidget(self.scrollr)

        self.R = [''] * self.Cir.lengthr    # Label to display resistor name
        self.Rtol = [''] * self.Cir.lengthr  # Label to display resistor name
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

        self.plot(mode)

    def plot(self, mode=None):
        logger.info('Plot')
        if self.x == []:
            logger.warning('Nothing to plot')
            return

        self.MplWidget.figure.clear()
        self.ax = self.MplWidget.figure.add_subplot(111)
        self.ax.set_title(f"Tolerance Analysis of {self.Cir.basename}")
        self.ax.grid()

        if mode == 'Opamp':
            self.line1 = []
            self.line1.append(self.ax.plot(self.x[0], self.y[0], label=self.Cir.opselect))
            for i in range(1, np.shape(self.y)[0]):
                self.line1.append(self.ax.plot(self.x[i], self.y[i], label=self.Cir.opamp[i - 1]))
            if self.Cir.simmode:
                self.ax.set_xlabel('Frequency/Hz')
                self.ax.set_ylabel('Gain/dB')
                self.ax.set_xscale('log')
            else:
                self.ax.set_xlabel('Time/s')
                self.ax.set_ylabel('Voltage/V')
            self.ax.legend()
            self.MplWidget.canvas.draw()
            return

        self.line1 = self.ax.plot(self.x, self.y)

        if mode == 'Step':  # Step mode is selected
            if len(self.x) < 25:
                line = self.line1.pop(0)    # Delete line on the graph
                line.remove()
                self.line1 = self.ax.plot(self.x, self.y, marker='x')

            self.ax.set_xlabel(f'{self.Cir.compselect}/{self.__unit}')
            if self.Cir.measmode == 'Cutoff Frequency':
                self.ax.set_ylabel('Cutoff Frequency/Hz')
            elif self.Cir.measmode == 'Cutoff Frequency Phase':
                self.ax.set_ylabel('Phase/rad')
            elif self.Cir.measmode == 'Gain Ripple':
                self.ax.set_ylabel('Gain Ripple/dB')
            else:
                self.ax.set_ylabel('Gain/dB')
            self.MplWidget.canvas.draw()
        elif 'CMRR' in mode:
            self.ax.set_xlabel('CMRR/dB')
            self.ax.set_ylabel('CDF')
            self.plotwst()  # Plot worst case
        else:
            if self.Cir.measmode == 'Cutoff Frequency':
                self.ax.set_xlabel('Cutoff Frequency/Hz')
            elif self.Cir.measmode == 'Cutoff Frequency Phase':
                self.ax.set_xlabel('Phase/rad')
            elif self.Cir.measmode == 'Gain Ripple':
                self.ax.set_xlabel('Gain Ripple/dB')
            else:
                self.ax.set_xlabel('Gain/dB')
            self.ax.set_ylabel('CDF')
            self.plotwst()  # Plot worst case

        self.MplWidget.figure.savefig(os.path.join(self.root, 'src/report/static/fig.svg'), format='svg', bbox_inches='tight')

    def plotwst(self):
        logger.info('wst')
        if self.x == []:
            return

        try:
            self.ax.get_legend().remove()    # Delete legend
            line = self.line2.pop(0)    # Delete line
            line.remove()
        except:
            pass

        if self.wstcase.isChecked():    # If check box of the worst case is checked
            self.line2 = self.ax.plot([self.Cir.wst_cutoff[0], self.Cir.wst_cutoff[-1]], [0, 1], 'xr')
            self.ax.legend([self.line2[0]], ['Worst Case'])

        self.MplWidget.canvas.draw()

    def AddTime(self):
        self.Cir.mc_runs = int(self.addtimetext.text())
        logger.info(f'Added:{self.Cir.mc_runs}')
        if self.configGUI.tabWidget.currentIndex() == 2:
            self.Cir.create_cmrr(add=True)
            self.start_process('CMRR-Add')
        else:
            self.Cir.create_sp(add=True)
            self.start_process('Add')

    # Calculate probability based on the probe input at bottom right corner

    def calcp(self):
        try:
            fc = float(self.calctext.text())
        except SyntaxError:
            self.presult.setText('Result: SyntaxError')
            return
        except:
            return
        larsmll = self.psign.currentText()
        unit = self.fcunit.currentIndex()

        if self.x == []:
            return
        else:
            # Convert to SI unit
            if 'Hz' in self.fcunit.currentText():
                fc = fc * 10**(unit * 3)
            elif 'F' in self.fcunit.currentText():
                fc = fc * 10**(unit * 3 - 12)
            elif 'Ω' in self.fcunit.currentText():  # dB no need to change
                fc = fc * 10**(unit * 3 - 3)

        if self.Cir.analmode == 1:  # Step mode
            if fc < self.x[0] or fc > self.x[-1]:   # Out of range
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

    # Analysis button is clicked
    def analy(self):
        self.configGUI.show()
        reconnect(self.configGUI.rejected, None, None)

    def reset(self):
        logger.info('Reset')
        self.ax.get_legend().remove()
        try:
            for i in range(len(self.line1)):
                line = self.line1[i].pop(0)
                line.remove()
        except IndexError:
            pass
        try:
            for i in range(len(self.line2)):
                line = self.line2[i].pop(0)
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
