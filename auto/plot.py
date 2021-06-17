from PyQt5.QtGui import QIntValidator
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
import os,sys
from scipy import interpolate
from PyQt5 import QtCore, QtWidgets,uic
import random

def plotcdf():
    with open('fc', "r") as fileobject:
        lines=fileobject.readlines()
    file1=[]
    row=[]
    for line in lines:
        row=line.split()
        file1.append(row)

    # col1=[]
    col2=[]
    for row0 in file1:
        # col1.append(row0[0])
        col2.append(row0[1])

    # del col1[0]
    del col2[0]

    length=len(col2)
    # cout=np.zeros(length)
    cutoff=np.zeros(length)

    for i in range(length):
        # cout[i]=float(col1[i])
        cutoff[i]=float(col2[i])

    # index=cutoff.argsort()
    cutoff=list(set(cutoff))
    length=len(cutoff)
    cutoff.sort()

    xaxis=np.linspace(cutoff[0],cutoff[-1],length)
    yaxis=np.arange(1,1+length)/length
    return cutoff,yaxis

    smooth=interpolate.interp1d(cutoff,yaxis,kind='cubic')

    # fig=plt.figure()
    # ax=plt.gca()

    plt.title("Cdf of Cutoff Frequency")
    plt.xlabel("Cutoff Frequency/Hz")
    plt.ylabel("Cdf")
    plt.grid()
    plt.plot(cutoff,smooth(cutoff),'b',cutoff,yaxis+0.1,'r')
    plt.show()




class Window(QtWidgets.QDialog):

    # constructor
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that
        # displays the 'figure'it takes the
        # 'figure' instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.runtime = QtWidgets.QLabel('Add simulation time:')
        self.runtimeadd = QtWidgets.QLineEdit()
        self.runtimeadd.setPlaceholderText('0')
        self.onlyInt = QIntValidator()
        self.runtimeadd.setValidator(self.onlyInt)
        self.runtimeadd.returnPressed.connect(self.changetime)

        self.totaltime = QtWidgets.QLabel('Total simulation time:')
        self.totaltimeadd = QtWidgets.QLineEdit()
        self.totaltimeadd.setPlaceholderText('1000')
        self.totaltimeadd.setValidator(self.onlyInt)
        self.totaltimeadd.returnPressed.connect(self.changetimet)

        # Just some button connected to 'plot' method
        self.button = QtWidgets.QPushButton('Plot')

        # adding action to the button
        # self.button.clicked.connect(self.plot)

        # creating a Vertical Box layout
        layout = QtWidgets.QGridLayout()

        # adding tool bar to the layout
        layout.addWidget(self.toolbar,0,0)

        # adding canvas to the layout
        layout.addWidget(self.canvas,1,0)

        # adding push button to the layout
        layout.addWidget(self.button,2,0)

        layout.addWidget(self.runtime,1,1)

        layout.addWidget(self.runtimeadd,1,2)

        layout.addWidget(self.totaltime,2,1)

        layout.addWidget(self.totaltimeadd,2,2)

        # setting layout to the main window
        self.setLayout(layout)

    def changetime(self):
        num=self.runtimeadd.text()
        print(f'changed:{num}\n')

    def changetimet(self):
        num=self.totaltimeadd.text()
        print(f'changed:{num}\n')

    # action called by thte push button
    def plot(self):
        print('Plot')
        # random data
        x,y=plotcdf()

        # clearing old figure
        self.figure.clear()

        # create an axis
        ax = self.figure.add_subplot(111)

        # plot data
        ax.plot(x,y)

        plt.title("Cdf of Cutoff Frequency")
        plt.xlabel("Cutoff Frequency/Hz")
        plt.ylabel("Cdf")
        plt.grid()

        # refresh canvas
        self.canvas.draw()


# class plotGUI(QtWidgets.QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.ui=uic.loadUi('main.ui')
#         self.ui.button.clicked.connect(self.handleCalc)

#     def handleCalc(self):
#         print('Clicked')

app=QtWidgets.QApplication(sys.argv)
main=Window()
main.show()
# gui=plotGUI()
# gui.ui.show()
app.exec_()