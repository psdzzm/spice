import subprocess
import numpy as np
from .Logging import logger
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5 import QtWidgets, uic, QtCore
from quantiphy import Quantity
import os
import shutil

# Processing... window


class processing(QtWidgets.QDialog):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    def __init__(self):
        super().__init__()
        uic.loadUi('../src/processing.ui', self)    # Load ui file
        self.setWindowTitle('Processing')
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose)


# Configuration window
class config(QtWidgets.QDialog):

    def __init__(self, root):
        super().__init__()

        uic.loadUi(root + '/src/config.ui', self)
        self.root = root

        self.barlayout = QtWidgets.QHBoxLayout(self.widget)
        self.bar = NavigationToolbar(self.MplWidget.canvas, self)
        self.barlayout.addWidget(self.bar)
        self.setWindowTitle('Configuration')
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.widget_4.setHidden(True)
        self.widget_7.setHidden(True)
        self.widget_8.setHidden(True)

        self.measnode.currentTextChanged.connect(self.netchange)
        self.measnode_2.currentTextChanged.connect(self.netchange)
        self.inputnode.currentTextChanged.connect(self.netchange)
        self.outputnode.currentTextChanged.connect(self.netchange)

        self.analmode.currentTextChanged.connect(self.analchange)
        self.analmode_2.currentTextChanged.connect(self.analchange)
        self.measmode.currentTextChanged.connect(self.analchange)
        self.simmode.currentTextChanged.connect(self.opampmode)
        self.stepcomp.currentTextChanged.connect(self.compchange)
        self.replace.currentTextChanged.connect(self.replacenum)

        self.open1.clicked.connect(self.opampopen)
        self.open2.clicked.connect(self.opampopen)
        self.open3.clicked.connect(self.opampopen)
        self.open4.clicked.connect(self.opampopen)
        self.open5.clicked.connect(self.opampopen)
        self.clear1.clicked.connect(self.opampdel)
        self.clear2.clicked.connect(self.opampdel)
        self.clear3.clicked.connect(self.opampdel)
        self.clear4.clicked.connect(self.opampdel)
        self.clear5.clicked.connect(self.opampdel)

        self.scroll = QtWidgets.QVBoxLayout(self.tab2)

    # Initialize the configuration window, require initialized circuit class instance parameter
    def init(self, Cir):
        self.Cir = Cir
        self.tab2UI()

        self.totaltime.setValue(1000 * (Cir.lengthc + Cir.lengthr))
        self.cmrrtime.setValue(self.totaltime.value())
        self.measnode.currentTextChanged.disconnect()
        self.measnode.clear()
        self.measnode.addItems(self.Cir.net)
        self.measnode.currentTextChanged.connect(self.netchange)
        self.measnode_2.currentTextChanged.disconnect()
        self.measnode_2.clear()
        self.measnode_2.addItems(self.Cir.net)
        self.measnode_2.currentTextChanged.connect(self.netchange)
        self.rfnum.setSpecialValueText('LAST')
        self.risefall.setCurrentIndex(1)

        self.inputnode.currentTextChanged.disconnect()
        self.inputnode.clear()
        self.inputnode.addItems(self.Cir.net)
        self.inputnode.currentTextChanged.connect(self.netchange)
        self.outputnode.currentTextChanged.disconnect()
        self.outputnode.clear()
        self.outputnode.addItems(self.Cir.net)
        self.outputnode.currentTextChanged.connect(self.netchange)

        self.opamp.clear()
        self.opamp.addItems(self.Cir.op)

        self.stepcomp.currentTextChanged.disconnect()
        self.stepcomp.clear()
        for i in range(Cir.lengthc):
            self.stepcomp.addItem(Cir.alter_c[i].name)
        for i in range(Cir.lengthr):
            self.stepcomp.addItem(Cir.alter_r[i].name)
        self.stepcomp.currentTextChanged.connect(self.compchange)

        self.CompValue.setText(f"Original Value: {Quantity(self.Cir.alter_c[0].c,units='F').render()}")

        self.compchange()
        self.replacenum()
        self.opampmode()

        if hasattr(Cir, 'startac'):
            temp = setunit(Cir.startac, 0, 4)
            self.startac.setValue(temp[0])
            self.startac_5.setValue(temp[0])
            self.startunit.setCurrentIndex(temp[1])
            self.startunit_5.setCurrentIndex(temp[1])
            temp = setunit(Cir.stopac, 0, 4)
            self.stopac.setValue(temp[0])
            self.stopac_5.setValue(temp[0])
            self.stopunit.setCurrentIndex(temp[1])
            self.stopunit_5.setCurrentIndex(temp[1])

        if hasattr(Cir, 'netselect'):
            try:
                self.measnode.setCurrentIndex(Cir.net.index(Cir.netselect))
            except:
                logger.exception()

        self.__node = 0

        self.MplWidget.figure.clear()
        self.ax = self.MplWidget.figure.add_subplot(111)
        self.ax.set_xscale('log')
        self.line1 = self.ax.plot(self.Cir.initx, self.Cir.inity[0, :])
        self.ax.set_title(f"Default AC Analysis of {self.Cir.basename}")
        self.ax.grid()
        self.ax.set_xlabel('Cutoff Frequency/Hz')
        self.ax.set_ylabel('vdb')

        self.MplWidget.canvas.draw()
        self.show()

    # Node to measure in Configuration window changes, update the matplotlib figure
    def netchange(self):
        self.__lastnode = self.__node
        self.__node = self.sender().currentIndex()
        self.ax.clear()
        self.ax.set_xscale('log')
        self.ax.grid()
        if self.tabWidget.currentIndex() == 2:
            with open('test.cir', 'w') as f:
                f.write(self.Cir.testtext[:-4])
                f.write(f"Vdiff000 {self.inputnode.currentText()} 0 AC 1\n.control\n\tsave {self.outputnode.currentText()}\n\tset wr_vecnames\n\tac dec 40 1 1G\n\tlet vout=1/V({self.outputnode.currentText()})\n\tlet vout=vdb(vout)\n\twrdata fc vout\n.endc\n\n.end")
            subprocess.run('ngspice -b test.cir -o test_log', shell=True, stdout=subprocess.DEVNULL)

            f = open('test_log')
            if 'error' in f.read().lower():
                QtWidgets.QMessageBox.critical(self, 'Error!', 'Error when measuring CMRR')
                self.sender().blockSignals(True)
                self.sender().setCurrentIndex(self.__lastnode)
                self.sender().blockSignals(False)
                self.__node = self.__lastnode
                f.close()
                os.remove('test_log')
                return

            f.close()
            os.remove('test_log')
            logger.debug(self.__lastnode)
            f = open('fc')
            f.readline()
            data = f.readlines()
            f.close()
            length = len(data)
            x, y = np.zeros(length), np.zeros(length)
            for line, i in zip(data, range(length)):
                x[i], y[i] = line.split()
            self.line1 = self.ax.plot(x, y)
            self.ax.set_title(f"Default CMRR Analysis of {self.Cir.basename}")
            self.ax.set_xlabel('Frequency/Hz')
            self.ax.set_ylabel('CMRR/dB')
            self.MplWidget.canvas.draw()
            return

        self.line1 = self.ax.plot(self.Cir.initx, self.Cir.inity[self.__node, :])
        self.ax.set_title(f"Default AC Analysis of {self.Cir.basename}")
        self.ax.set_xlabel('Cutoff Frequency/Hz')
        self.ax.set_ylabel('vdb')
        self.MplWidget.canvas.draw()

    # Simulation mode changes
    def analchange(self):
        if self.analmode.currentIndex() == 1:   # Simulation mode is Step
            self.tabWidget.setTabVisible(1, False)  # Set tab2 to invisible as no tolerance is needed
            self.widget_8.setHidden(False)
            self.label_2.setHidden(True)
            self.totaltime.setHidden(True)
            mode = self.analmode_2.currentIndex()   # Step type is linear to list
            if mode == 0:   # Linear
                self.widget_4.setHidden(True)
                self.widget_7.setHidden(False)
            else:           # List
                self.widget_4.setHidden(False)
                self.widget_7.setHidden(True)
        else:   # Simulation mode is ac analysis
            self.tabWidget.setTabVisible(1, True)
            self.label_2.setHidden(False)
            self.totaltime.setHidden(False)
            self.widget_4.setHidden(True)
            self.widget_7.setHidden(True)
            self.widget_8.setHidden(True)

        mode = self.measmode.currentIndex()  # Get Measure mode
        if mode < 2:   # Measure mode is cutoff frequency or phase
            self.widget_5.setHidden(False)
        else:
            self.widget_5.setHidden(True)

    # Component to alter in step mode changes

    def compchange(self):
        index = self.stepcomp.currentIndex()

        # Change unit based on component type
        if index < self.Cir.lengthc:    # Capacitor
            q = Quantity(self.Cir.alter_c[index].c, units='F')  # Get standard component value
            temp = setunit(q.real, -12, 5)  # samllest unit is pF, base = -12, have 5 units, see function definition for more detail
            self.CompValue.setText(f"Original Value: {q.render()}")
            if 'F' not in self.startunit_2.currentText():   # Update unit list
                self.startunit_2.clear()
                self.stopunit_2.clear()
                self.increunit_2.clear()
                self.startunit_2.addItems(['pF', 'nF', 'μF', 'mF', 'F'])
                self.stopunit_2.addItems(['pF', 'nF', 'μF', 'mF', 'F'])
                self.increunit_2.addItems(['pF', 'nF', 'μF', 'mF', 'F'])

        elif index >= self.Cir.lengthc:  # Component selected is resistor
            q = Quantity(self.Cir.alter_r[index - self.Cir.lengthc].r, units='Ω')
            temp = setunit(q.real, -3, 4)
            self.CompValue.setText(f"Original Value: {q.render()}")
            if 'Ω' not in self.stepcomp.currentText():
                self.startunit_2.clear()
                self.stopunit_2.clear()
                self.increunit_2.clear()
                self.startunit_2.addItems(['mΩ', 'Ω', 'kΩ', 'MΩ'])
                self.stopunit_2.addItems(['mΩ', 'Ω', 'kΩ', 'MΩ'])
                self.increunit_2.addItems(['mΩ', 'Ω', 'kΩ', 'MΩ'])

        # Update alter list in linear mode
        self.startac_2.setValue(temp[0])
        self.stopac_2.setValue(temp[0])
        self.stopac_3.setValue(temp[0] / 10)
        self.startunit_2.setCurrentIndex(temp[1])
        self.stopunit_2.setCurrentIndex(temp[1])
        self.increunit_2.setCurrentIndex(temp[1])

    def opampmode(self):
        if self.simmode.currentIndex():
            self.startunit_5.clear()
            self.stopunit_5.clear()
            self.startunit_5.addItems(['Hz', 'kHz', 'MHz', 'GHz'])
            self.stopunit_5.addItems(['Hz', 'kHz', 'MHz', 'GHz'])
        else:
            self.startunit_5.clear()
            self.stopunit_5.clear()
            self.startunit_5.addItems(['ns', 'μs', 'ms', 's'])
            self.stopunit_5.addItems(['ns', 'μs', 'ms', 's'])

    def replacenum(self):
        num = int(self.replace.currentText())
        widget = [self.first, self.second, self.third, self.fourth, self.fifth]
        for i in range(num):
            widget[i].setHidden(False)
        for i in range(num, 5):
            widget[i].setHidden(True)

    def opampopen(self):
        if not hasattr(self.Cir, 'opamp'):
            self.Cir.opamp = [None] * 5
            self.Cir.opampfilename = [None] * 5

        widget = [self.opened1, self.opened2, self.opened3, self.opened4, self.opened5]
        i = int(self.sender().objectName()[-1]) - 1
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', self.root + '/CirFile', "Subcircuit File (*)")
        if fname:
            self.Cir.opampfilename[i] = os.path.basename(fname)
            if os.path.isfile(self.Cir.opampfilename[i]):
                QtWidgets.QMessageBox.critical(self, 'Error', f'File {self.Cir.opampfilename[i]} already exists')
                return

            with open(fname) as f:
                for line in f:
                    if line.upper().startswith('.SUBCKT '):
                        if line.split()[1] in self.Cir.opampfilename:
                            QtWidgets.QMessageBox.critical(self, 'Error', 'Duplicate subcircuit!')
                            return
                        else:
                            self.Cir.opamp[i] = line.split()[1]
                            logger.debug(self.Cir.opamp[i])
                            break

            widget[i].setText(self.Cir.opampfilename[i] + ' - ' + self.Cir.opamp[i])
            shutil.copyfile(fname, os.path.join(os.getcwd(), self.Cir.opampfilename[i]))

    def opampdel(self):
        widget = [self.opened1, self.opened2, self.opened3, self.opened4, self.opened5]
        i = int(self.sender().objectName()[-1]) - 1
        if widget[i].text():
            widget[i].clear()
            os.remove(self.Cir.opampfilename[i])
            self.Cir.opamp[i] = None
            self.Cir.opampfilename[i] = None

    # Initialize tab2: tolerance

    def tab2UI(self):
        # Delete all existing widget in tab2
        for i in reversed(range(self.scroll.count())):
            self.scroll.itemAt(i).widget().deleteLater()

        self.scrollc = QtWidgets.QScrollArea(self.tab2)
        self.scrollc.setMaximumSize(QtCore.QSize(250, 250))
        self.layoutWidgetc = QtWidgets.QWidget(self.scrollc)

        self.C = [''] * self.Cir.lengthc
        self.Ctol = [''] * self.Cir.lengthc
        self.formLayoutc = QtWidgets.QFormLayout(self.layoutWidgetc)
        self.Mapper = QtCore.QSignalMapper(self)
        for i in range(self.Cir.lengthc):
            self.C[i] = QtWidgets.QLabel(f'{self.Cir.alter_c[i].name}', self.layoutWidgetc)
            self.Ctol[i] = QtWidgets.QDoubleSpinBox(self.layoutWidgetc)
            self.Ctol[i].setValue(self.Cir.alter_c[i].tol)
            reconnect(self.Ctol[i].valueChanged, self.Mapper.map)
            self.Mapper.setMapping(self.Ctol[i], f'C{i}')
            self.Ctol[i].setSingleStep(0.01)
            self.Ctol[i].setMaximum(0.9999)
            self.Ctol[i].setDecimals(4)
            self.Ctol[i].setMaximumWidth(85)
            self.formLayoutc.setWidget(i + 2, QtWidgets.QFormLayout.LabelRole, self.C[i])
            self.formLayoutc.setWidget(i + 2, QtWidgets.QFormLayout.FieldRole, self.Ctol[i])

        self.titleC = QtWidgets.QLabel('Capacitor', self.layoutWidgetc)
        self.titleC.setAlignment(QtCore.Qt.AlignCenter)
        self.formLayoutc.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.titleC)
        self.checkC = QtWidgets.QCheckBox('Same Tolerance', self.layoutWidgetc)
        reconnect(self.checkC.toggled, self.sametol)
        self.formLayoutc.setWidget(1, QtWidgets.QFormLayout.SpanningRole, self.checkC)
        self.scrollc.setWidget(self.layoutWidgetc)
        self.scrollc.setAlignment(QtCore.Qt.AlignHCenter)
        self.scroll.addWidget(self.scrollc)

        self.scrollr = QtWidgets.QScrollArea(self.tab2)
        self.scrollr.setMaximumSize(QtCore.QSize(250, 250))
        self.layoutWidgetr = QtWidgets.QWidget(self.scrollr)

        self.R = [''] * self.Cir.lengthr
        self.Rtol = [''] * self.Cir.lengthr
        self.formLayoutr = QtWidgets.QFormLayout(self.layoutWidgetr)
        for i in range(self.Cir.lengthr):
            self.R[i] = QtWidgets.QLabel(f'{self.Cir.alter_r[i].name}', self.layoutWidgetr)
            self.Rtol[i] = QtWidgets.QDoubleSpinBox(self.layoutWidgetr)
            self.Rtol[i].setValue(self.Cir.alter_r[i].tol)
            reconnect(self.Rtol[i].valueChanged, self.Mapper.map)
            self.Mapper.setMapping(self.Rtol[i], f'R{i}')
            self.Rtol[i].setSingleStep(0.01)
            self.Rtol[i].setMaximum(0.9999)
            self.Rtol[i].setDecimals(4)
            self.Rtol[i].setMaximumWidth(85)
            self.formLayoutr.setWidget(i + 2, QtWidgets.QFormLayout.LabelRole, self.R[i])
            self.formLayoutr.setWidget(i + 2, QtWidgets.QFormLayout.FieldRole, self.Rtol[i])

        reconnect(self.Mapper.mappedString, self.sametol)
        self.titleR = QtWidgets.QLabel('Resistor', self.layoutWidgetr)
        self.titleR.setAlignment(QtCore.Qt.AlignCenter)
        self.formLayoutr.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.titleR)
        self.checkR = QtWidgets.QCheckBox('Same Tolerance', self.layoutWidgetr)
        reconnect(self.checkR.toggled, self.sametol)
        self.formLayoutr.setWidget(1, QtWidgets.QFormLayout.SpanningRole, self.checkR)
        self.scrollr.setWidget(self.layoutWidgetr)
        self.scrollr.setAlignment(QtCore.Qt.AlignHCenter)
        self.scroll.addWidget(self.scrollr)
        self.scroll.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

    # Set component tolerance to the same

    def sametol(self, i):
        if self.sender() is self.checkC:    # If checkbox for capacitor is checked
            for i in range(1, self.Cir.lengthc):
                self.Ctol[i].setValue(self.Ctol[0].value())
        elif self.sender() is self.checkR:  # If checkbox for resistor is checked
            for i in range(1, self.Cir.lengthr):
                self.Rtol[i].setValue(self.Rtol[0].value())
        elif i[0] == 'C':       # Tolerance of capacitor is changed
            i = int(i[1:])      # Get which capacitor is changed
            if self.checkC.isChecked():    # checkbox for capacitor is checked
                k = list(range(self.Cir.lengthc))
                k.remove(i)
                for j in k:
                    self.Ctol[j].blockSignals(True)     # Block signal sending
                    self.Ctol[j].setValue(self.Ctol[i].value())
                    self.Ctol[j].blockSignals(False)
        elif i[0] == 'R':   # Tolerance of resistor is changed
            i = int(i[1:])  # Get which resistor is changed
            if self.checkR.isChecked():     # checkbox for resistor is checked
                k = list(range(self.Cir.lengthr))
                k.remove(i)
                for j in k:
                    self.Rtol[j].blockSignals(True)
                    self.Rtol[j].setValue(self.Rtol[i].value())
                    self.Rtol[j].blockSignals(False)


# Reconnect pyqt handler
def reconnect(signal, newhandler=None, oldhandler=None):
    try:    # Disconnect all old signals
        if oldhandler is None:
            signal.disconnect()
        else:
            while True:
                signal.disconnect(oldhandler)
    except TypeError:   # No old signal is connected
        pass
    finally:    # Connect to new handler
        if newhandler is not None:
            signal.connect(newhandler)


'''
Calculate value based on unit
value: standard value in SI
base: the smallest unit. For explame, if nF is the smallest, base is -9 as n is 10^-9
level: how many units are available. For example: nF, uF, mF, F ,then level = 4
'''


def setunit(value, base, level):
    for i in range(level):
        if value < 10**(base + 3 * i + 3):
            return value / 10**(base + 3 * i), i

    return value / 10**(base + 3 * i), i
