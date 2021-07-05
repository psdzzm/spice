from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5 import QtWidgets, uic, QtCore


class processing(QtWidgets.QDialog):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    def __init__(self):
        super().__init__()
        uic.loadUi('../src/processing.ui', self)
        self.setWindowTitle('Processing')
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        # self.show()


class config(QtWidgets.QDialog):

    def __init__(self, Cir, root):
        super().__init__()

        self.Cir = Cir
        uic.loadUi(root+'/src/config.ui', self)
        self.tab2UI()
        self.barlayout = QtWidgets.QHBoxLayout(self.widget)
        self.bar = NavigationToolbar(self.MplWidget.canvas, self)
        self.barlayout.addWidget(self.bar)
        self.setWindowTitle('Configuration')
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.totaltime.setValue(100)
        self.measnode.addItems(Cir.net)
        self.rfnum.setSpecialValueText('LAST')
        self.risefall.setCurrentIndex(1)
        # self.tolcolor()

        # self.buttonBox.setDefault(False)
        # self.buttonBox.setAutoDefault(False)

        self.measnode.currentTextChanged.connect(self.netchange)

        self.analmode.currentTextChanged.connect(self.analchange)

        self.measmode.currentTextChanged.connect(self.showhide)

        self.MplWidget.figure.clear()

        self.ax = self.MplWidget.figure.add_subplot(111)
        self.ax.set_xscale('log')
        self.line1 = self.ax.plot(self.Cir.initx, self.Cir.inity[0, :])
        self.ax.set_title(f"Default AC Analysis of {self.Cir.shortname}")
        self.ax.grid()
        self.ax.set_xlabel('Cutoff Frequency/Hz')
        self.ax.set_ylabel('vdb')

        self.show()

    def netchange(self):
        node = self.measnode.currentIndex()
        # line = self.line1.pop(0)
        # line.remove()
        self.ax.clear()
        self.ax.set_xscale('log')
        self.line1 = self.ax.plot(self.Cir.initx, self.Cir.inity[node, :])
        self.ax.set_title(f"Default AC Analysis of {self.Cir.shortname}")
        self.ax.grid()
        self.ax.set_xlabel('Cutoff Frequency/Hz')
        self.ax.set_ylabel('vdb')
        self.MplWidget.canvas.draw()

    def analchange(self):
        mode = self.analmode.currentIndex()
        if mode == 0:
            self.widget_3.setHidden(False)
        else:
            self.widget_3.setHidden(True)

    def showhide(self):
        mode = self.measmode.currentIndex()
        if mode == 0:
            self.widget_5.setHidden(False)
        else:
            self.widget_5.setHidden(True)

    def tab2UI(self):
        self.scroll = QtWidgets.QVBoxLayout()

        self.scrollc = QtWidgets.QScrollArea()
        self.scrollc.setMaximumSize(QtCore.QSize(250, 250))
        self.layoutWidgetc = QtWidgets.QWidget(self.scrollc)

        self.C = ['']*self.Cir.lengthc
        self.Ctol = ['']*self.Cir.lengthc
        self.formLayoutc = QtWidgets.QFormLayout(self.layoutWidgetc)
        self.Mapper = QtCore.QSignalMapper(self)
        for i in range(self.Cir.lengthc):
            self.C[i] = QtWidgets.QLabel(
                f'{self.Cir.alter_c[i].name}', self.layoutWidgetc)
            self.Ctol[i] = QtWidgets.QDoubleSpinBox(self.layoutWidgetc)
            self.Ctol[i].setValue(self.Cir.alter_c[i].tol)
            # self.Ctol[i].valueChanged.connect(self.tolcolor)
            self.Ctol[i].valueChanged.connect(self.Mapper.map)
            self.Mapper.setMapping(self.Ctol[i], f'C{i}')
            self.Ctol[i].setSingleStep(0.01)
            self.Ctol[i].setMaximum(0.9999)
            self.Ctol[i].setDecimals(4)
            self.Ctol[i].setMaximumWidth(85)
            self.formLayoutc.setWidget(
                i+2, QtWidgets.QFormLayout.LabelRole, self.C[i])
            self.formLayoutc.setWidget(
                i+2, QtWidgets.QFormLayout.FieldRole, self.Ctol[i])

        self.titleC = QtWidgets.QLabel('Capacitor', self.layoutWidgetc)
        self.titleC.setAlignment(QtCore.Qt.AlignCenter)
        self.formLayoutc.setWidget(
            0, QtWidgets.QFormLayout.SpanningRole, self.titleC)
        self.checkC = QtWidgets.QCheckBox('Same Tolerance', self.layoutWidgetc)
        self.checkC.toggled.connect(self.sametol)
        self.formLayoutc.setWidget(
            1, QtWidgets.QFormLayout.SpanningRole, self.checkC)
        self.scrollc.setWidget(self.layoutWidgetc)
        self.scrollc.setAlignment(QtCore.Qt.AlignHCenter)
        self.scroll.addWidget(self.scrollc)
        self.scrollr = QtWidgets.QScrollArea()
        self.scrollr.setMaximumSize(QtCore.QSize(250, 250))
        self.layoutWidgetr = QtWidgets.QWidget(self.scrollr)

        self.R = ['']*self.Cir.lengthr
        self.Rtol = ['']*self.Cir.lengthr
        self.formLayoutr = QtWidgets.QFormLayout(self.layoutWidgetr)
        for i in range(self.Cir.lengthr):
            self.R[i] = QtWidgets.QLabel(
                f'{self.Cir.alter_r[i].name}', self.layoutWidgetr)
            self.Rtol[i] = QtWidgets.QDoubleSpinBox(self.layoutWidgetr)
            self.Rtol[i].setValue(self.Cir.alter_r[i].tol)
            # self.Rtol[i].valueChanged.connect(self.tolcolor)
            self.Rtol[i].valueChanged.connect(self.Mapper.map)
            self.Mapper.setMapping(self.Rtol[i], f'R{i}')
            self.Rtol[i].setSingleStep(0.01)
            self.Rtol[i].setMaximum(0.9999)
            self.Rtol[i].setDecimals(4)
            self.Rtol[i].setMaximumWidth(85)
            self.formLayoutr.setWidget(
                i+2, QtWidgets.QFormLayout.LabelRole, self.R[i])
            self.formLayoutr.setWidget(
                i+2, QtWidgets.QFormLayout.FieldRole, self.Rtol[i])

        self.Mapper.mappedString.connect(self.sametol)
        self.titleR = QtWidgets.QLabel('Resistor', self.layoutWidgetr)
        self.titleR.setAlignment(QtCore.Qt.AlignCenter)
        self.formLayoutr.setWidget(
            0, QtWidgets.QFormLayout.SpanningRole, self.titleR)
        self.checkR = QtWidgets.QCheckBox('Same Tolerance', self.layoutWidgetr)
        self.checkR.toggled.connect(self.sametol)
        self.formLayoutr.setWidget(
            1, QtWidgets.QFormLayout.SpanningRole, self.checkR)
        self.scrollr.setWidget(self.layoutWidgetr)
        self.scrollr.setAlignment(QtCore.Qt.AlignHCenter)
        self.scroll.addWidget(self.scrollr)
        self.scroll.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

        self.tab2.setLayout(self.scroll)

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

    def sametol(self, i):
        if self.sender() is self.checkC:
            for i in range(1, self.Cir.lengthc):
                self.Ctol[i].setValue(self.Ctol[0].value())
        elif self.sender() is self.checkR:
            for i in range(1, self.Cir.lengthr):
                self.Rtol[i].setValue(self.Rtol[0].value())
        elif i[0] == 'C':
            i = int(i[1:])
            if self.checkC.isChecked():
                k = list(range(self.Cir.lengthc))
                k.remove(i)
                for j in k:
                    self.Ctol[j].blockSignals(True)
                    self.Ctol[j].setValue(self.Ctol[i].value())
                    self.Ctol[j].blockSignals(False)
        elif i[0] == 'R':
            i = int(i[1:])
            if self.checkR.isChecked():
                k = list(range(self.Cir.lengthr))
                k.remove(i)
                for j in k:
                    self.Rtol[j].blockSignals(True)
                    self.Rtol[j].setValue(self.Rtol[i].value())
                    self.Rtol[j].blockSignals(False)
