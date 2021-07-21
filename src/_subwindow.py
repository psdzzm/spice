from logging import Logger, exception
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5 import QtWidgets, uic, QtCore
from quantiphy import Quantity


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
        # self.show()


# Configuration window
class config(QtWidgets.QDialog):

    def __init__(self, root):
        super().__init__()

        uic.loadUi(root + '/src/config.ui', self)

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

        self.analmode.currentTextChanged.connect(self.analchange)

        self.analmode_2.currentTextChanged.connect(self.analchange)

        self.measmode.currentTextChanged.connect(self.analchange)

        self.stepcomp.currentTextChanged.connect(self.compchange)

        self.scroll = QtWidgets.QVBoxLayout(self.tab2)

    def init(self, Cir):
        self.Cir = Cir
        self.tab2UI()

        self.totaltime.setValue(1000 * (Cir.lengthc + Cir.lengthr))
        self.measnode.currentTextChanged.disconnect()
        self.measnode.clear()
        self.measnode.addItem('out')
        self.measnode.addItems(self.Cir.net)
        self.measnode.currentTextChanged.connect(self.netchange)
        self.rfnum.setSpecialValueText('LAST')
        self.risefall.setCurrentIndex(1)

        self.stepcomp.currentTextChanged.disconnect()
        self.stepcomp.clear()
        for i in range(Cir.lengthc):
            self.stepcomp.addItem(Cir.alter_c[i].name)
        for i in range(Cir.lengthr):
            self.stepcomp.addItem(Cir.alter_r[i].name)
        self.stepcomp.currentTextChanged.connect(self.compchange)

        self.CompValue.setText(f"Original Value: {Quantity(self.Cir.alter_c[0].c,units='F').render()}")

        if hasattr(Cir, 'startac'):
            temp = setunit(Cir.startac, 0, 4)
            self.startac.setValue(temp[0])
            self.startunit.setCurrentIndex(temp[1])
            temp = setunit(Cir.stopac, 0, 4)
            self.stopac.setValue(temp[0])
            self.stopunit.setCurrentIndex(temp[1])

        if hasattr(Cir, 'netselect'):
            try:
                if Cir.netselect == 'out':
                    pass
                else:
                    self.measnode.setCurrentIndex(Cir.net.index(Cir.netselect) + 1)
            except:
                Logger.exception()

        self.compchange()

        self.MplWidget.figure.clear()
        self.ax = self.MplWidget.figure.add_subplot(111)
        self.ax.set_xscale('log')
        self.line1 = self.ax.plot(self.Cir.initx, self.Cir.inity[0, :])
        self.ax.set_title(f"Default AC Analysis of {self.Cir.shortname}")
        self.ax.grid()
        self.ax.set_xlabel('Cutoff Frequency/Hz')
        self.ax.set_ylabel('vdb')

        self.MplWidget.canvas.draw()
        self.show()

    # Node to measure in Configuration window changes, update the matplotlib figure
    def netchange(self):
        node = self.measnode.currentIndex()
        self.ax.clear()
        self.ax.set_xscale('log')
        self.line1 = self.ax.plot(self.Cir.initx, self.Cir.inity[node, :])
        self.ax.set_title(f"Default AC Analysis of {self.Cir.shortname}")
        self.ax.grid()
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
        if mode == 0:   # Measure mode is cutoff frequency
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
