# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 01-07-2021 15:01:35
 LastEditors: Yichen Zhang
 LastEditTime: 01-07-2021 18:15:02
 FilePath: /circuit/Workspace/test/runtime.py
'''
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QPlainTextEdit, QVBoxLayout, QWidget)

from PyQt5.QtCore import QProcess
import sys,os

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.p = None

        self.btn = QPushButton("Execute")
        self.btn.pressed.connect(self.start_process)
        self.text = QPlainTextEdit()
        # self.text.setReadOnly(True)

        l = QVBoxLayout()
        l.addWidget(self.btn)
        l.addWidget(self.text)

        w = QWidget()
        w.setLayout(l)

        self.setCentralWidget(w)

    def message(self, s):
        self.text.appendPlainText(s)

    def start_process(self):
        if self.p is None:  # No process running.
            self.message("Executing process")
            self.p = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self.p.finished.connect(self.process_finished)
            # self.p.waitForFinished()
            self.p.start('/bin/bash',['-c',"ngspice -b run_control.sp run_control_wst.sp -o run_log"])
            self.p.readyReadStandardOutput.connect(self.handle_stdout)

    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message(stdout)
        os.system(f'sleep 1;kill {self.p.pid()}')

    def process_finished(self):
        self.message("Process finished.")
        self.p = None


os.chdir(os.path.dirname(os.path.abspath(__file__)))
app = QApplication(sys.argv)

w = MainWindow()
w.show()

app.exec_()