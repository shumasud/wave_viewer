# -*- coding: utf-8 -*-
"""
Name:
Purpose:
Specification:
Environment:
    Python 3.6.0

"""

import numpy as np
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import sys
import scipy.fftpack
from scipy import signal
import pandas as pd


class SpeAna(QtGui.QWidget):

    def __init__(self):
        super().__init__()

        self.time = None
        self.sig = None

        self.waveGraph = WaveGraph()

        self.tLabel = QtGui.QLabel('Time Interval [s]')
        self.tEdit = QtGui.QLineEdit('5E-6')
        self.tEdit.textChanged.connect(self.handleTime)

        self.fileBtn = QtGui.QPushButton('Open File')
        self.fileBtn.clicked.connect(self.showFileDialog)
        self.fileIdc = QtGui.QLineEdit('None')
        self.fileIdc.setReadOnly(True)

        self.adpLabel = QtGui.QLabel('Data of ')
        self.adpEdit = QtGui.QComboBox()
        self.adpEdit.addItem('Keyence')
        self.adpEdit.addItem('Hara')

        self.execBtn = QtGui.QPushButton("Analyze")
        self.execBtn.clicked.connect(self.execFFT)

        self.winLabel = QtGui.QLabel('Window')
        self.winEdit = QtGui.QComboBox()
        self.winEdit.addItem('Rect')
        self.winEdit.addItem('Hanning')

        grid = QtGui.QGridLayout()
        self.setLayout(grid)
        grid.addWidget(self.fileBtn, 0, 0)
        grid.addWidget(self.fileIdc, 0, 1)
        grid.addWidget(self.adpLabel, 0, 2)
        grid.addWidget(self.adpEdit, 0, 3)
        grid.addWidget(self.tLabel, 1, 0)
        grid.addWidget(self.tEdit, 1, 1)
        grid.addWidget(self.winLabel, 1, 2)
        grid.addWidget(self.winEdit, 1, 3)
        grid.addWidget(self.execBtn, 2, 0, 1, 4)
        grid.addWidget(self.waveGraph, 3, 0, 1, 4)

    def handleTime(self, text):
        try:
            dt = float(text)
            N = len(self.sig)
            self.time = np.arange(0, N*dt, dt)
            self.waveGraph.draw0(self.time, self.sig)
        except ValueError:
            pass

    def showFileDialog(self):
        fd = QtGui.QFileDialog()
        self.fName = fd.getOpenFileName()
        self.fileIdc.setText(self.fName)
        self.aqData()

    def aqData(self):
        if self.adpEdit.currentText() == 'Keyence':
            df = pd.read_csv(self.fName, encoding='cp932', header=None)
            self.sig = np.array(df.iloc[:, 2])
        elif self.adpEdit.currentText() == 'Hara':
            df = pd.read_csv(self.fName, encoding='cp932', header=None)
            self.sig = np.array(df.iloc[:, 5])
        N = len(self.sig)
        dt = float(self.tEdit.text())
        self.time = np.arange(0, N*dt, dt)
        self.waveGraph.draw0(self.time, self.sig)

    def execFFT(self):

        N = len(self.time)
        dt = float(self.tEdit.text())

        winName = self.winEdit.currentText()
        if winName == 'Rect':
            win = np.ones(N)
        elif winName == 'Hanning':
            win = signal.hann(N)

        fSig = scipy.fftpack.fft(self.sig * win)
        freq = scipy.fftpack.fftfreq(N, dt)
        ampSig = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in fSig]
        self.waveGraph.draw1(freq[:int(N/2)], ampSig[:int(N/2)])


class WaveGraph(pg.GraphicsWindow):

    def __init__(self):
        super().__init__()
        self.plot0 = self.addPlot(row=1, col=0)
        self.plot0.setLabels(bottom=('time', 's'), left=('signal', 'a.u.'))
        self.plot0.showGrid(x=True, y=True)
        self.plot1 = self.addPlot(row=1, col=1)
        self.plot1.setLabels(bottom=('frequency', 'Hz'), left=('intensity', 'a.u.'))
        self.plot1.showGrid(x=True, y=True)
        # self.plot1.setLogMode(y=True)

    def draw0(self, x, y):
        self.plot0.clear()
        self.plot0.plot(x, y, pen='r')

    def draw1(self, x, y):
        self.plot1.clear()
        self.plot1.plot(x, y, pen='r')



def main():
    app = QtGui.QApplication(sys.argv)
    speAna = SpeAna()
    speAna.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
