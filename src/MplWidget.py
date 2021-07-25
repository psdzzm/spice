# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description: Base of the matplotlib canvas for the main window and configuration window
 Author: Yichen Zhang
 Date: 19-07-2021 19:17:47
 LastEditors: Yichen Zhang
 LastEditTime: 25-07-2021 10:53:20
 FilePath: /circuit/src/MplWidget.py
'''
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib import pyplot as plt


class MplWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        self.setLayout(vertical_layout)
