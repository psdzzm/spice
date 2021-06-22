from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvas

from matplotlib import pyplot as plt


class MplWidget (QWidget):

    def __init__(self,  parent=None):

        QWidget . __init__(self,  parent)

        self.figure = plt.figure()

        self . canvas = FigureCanvas(self.figure)

        vertical_layout = QVBoxLayout()
        vertical_layout . addWidget(self . canvas)

        self . setLayout(vertical_layout)
