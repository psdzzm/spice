from src import plotGUI
from PyQt5 import QtWidgets
import os,sys


app = QtWidgets.QApplication(sys.argv)
main = plotGUI()
main.show()
app.exec_()
print(os.getcwd())