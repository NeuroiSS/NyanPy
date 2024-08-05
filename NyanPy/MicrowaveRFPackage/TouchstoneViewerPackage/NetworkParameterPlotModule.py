from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
from enum import StrEnum
import sys
import os
import numpy as np
import pyqtgraph as pg

from NetworkParameterModule import NetworkParameter, ParamTypes

# PyQtGraph Global Options
#pg.setConfigOptions(antialias=True)


class Diagrams(StrEnum):
    MAG = 'Mag'
    PHASE = 'Phase'
    MAG_PHASE = 'Mag & Phase'
    REAL = 'Re'
    IMAGINARY = 'Im'
    REAL_IMAGINARY = 'Re & Im'
    SMITH = 'Smith'
    ADMITTANCE_SMITH = 'Admit. Smith'
    POLAR = 'Polar'


class NetworkParameterPlot(QtWidgets.QWidget):

    def __init__(self, networks:list, parent = None):
        super().__init__(parent)
        self.__parameterComboBox = QtWidgets.QComboBox()
        self.__suffixComboBox = QtWidgets.QComboBox()
        self.__diagramComboBox = QtWidgets.QComboBox()
        self.__networks = networks
        self.__color = QtGui.QColor('#000000')
        self.__currentText = ''
        self.__hlPlots = []
        self.__graph = pg.GraphicsLayoutWidget()

        self.setupUi()
        self.connectSignals()

    def setColor(self, color):
        self.__color = QtGui.QColor(color)

    def setSuffix(self, suffix:str):
        self.__suffixComboBox.setCurrentText(suffix)

    def suffix(self):
        return self.__suffixComboBox.currentText()

    def parameterIndex(self):
        s = self.suffix()
        return (int(s[0]) - 1, int(s[1]) - 1)

    def setupUi(self):
        # Minimum size
        self.__parameterComboBox.setMinimumWidth(130)
        self.__suffixComboBox.setMinimumWidth(50)
        self.__diagramComboBox.setMinimumWidth(100)
        self.__graph.setMinimumSize(400, 250)

        # Populate comboboxes
        self.__parameterComboBox.addItems([item.value for item in ParamTypes])
        self.__suffixComboBox.addItems(['11', '12', '21', '22',\
                '13', '23', '31', '32', '33', '14', '24', '34', '41', '42', '43', '44'])
        self.__diagramComboBox.addItems([item.value for item in Diagrams])

        # Layouts
        hboxlayout = QtWidgets.QHBoxLayout()
        hboxlayout.addWidget(QtWidgets.QLabel('Parameter:'))
        hboxlayout.addWidget(self.__parameterComboBox)
        hboxlayout.addWidget(self.__suffixComboBox)
        hboxlayout.addWidget(QtWidgets.QLabel('Diagram:'))
        hboxlayout.addWidget(self.__diagramComboBox)
        hboxlayout.addStretch()
        hboxlayout.setContentsMargins(0, 0, 0, 0)
        hboxlayout.setSpacing(5)

        vboxlayout = QtWidgets.QVBoxLayout(self)
        vboxlayout.addLayout(hboxlayout)
        vboxlayout.addWidget(self.__graph)
        vboxlayout.setContentsMargins(5, 5, 5, 5)
        vboxlayout.setSpacing(5)

    def connectSignals(self):
        self.__parameterComboBox.currentIndexChanged.connect(self.plot)
        self.__suffixComboBox.currentIndexChanged.connect(self.plot)
        self.__diagramComboBox.currentIndexChanged.connect(self.plot)

    @Slot()
    def setCurrentText(self, text:str):
        self.__currentText = text
        self.hlPlot()

    def hlPlot(self):
        if not self.__currentText:
            return

        for item in self.__hlPlots:
            item.setPen(pg.mkPen(color=self.__color, width=2)\
                    if item.name() == self.__currentText\
                    else None)

    @Slot()
    def plot(self):
        paramType = ParamTypes(self.__parameterComboBox.currentText())
        diagram = Diagrams(self.__diagramComboBox.currentText())
        n, m = self.parameterIndex()
        
        # Clear
        self.__graph.clear()
        self.__hlPlots.clear()

        # Set background color
        self.__graph.setBackground(pg.getConfigOption('background'))

        #------------------------------------------------------------------------------------------
        # MAG PLOT
        #------------------------------------------------------------------------------------------
        if diagram == Diagrams.MAG:
            p = self.__graph.addPlot()
            p.setLabels(bottom='Frequency (Hz)', left=paramType.value+' (dB)')
            p.getAxis('left').setGrid(20)
            p.getAxis('bottom').setGrid(20)

            # Gray plots
            pen = pg.mkPen(color=self.__color.lighter(), width=1, style=Qt.DashLine)
            for network in self.__networks:
                vector = network.vector(paramType, n, m)
                if vector is None:
                    continue

                x = network.freq()
                y = 20. * np.log10(np.abs(vector))
                p.plot(x, y, pen=pen)

            # Highlight plots
            pen = None
            for network in self.__networks:
                vector = network.vector(paramType, n, m)
                if vector is None:
                    continue

                x = network.freq()
                y = 20. * np.log10(np.abs(vector))
                pItem = p.plot(x, y, pen=pen, name=network.text())
                self.__hlPlots.append(pItem)

            self.hlPlot()

        #------------------------------------------------------------------------------------------
        # PHASE PLOT
        #------------------------------------------------------------------------------------------
        elif diagram == Diagrams.PHASE:
            p = self.__graph.addPlot()
            p.setLabels(bottom='Frequency (Hz)', left=paramType.value+' (deg)')
            p.getAxis('left').setGrid(20)
            p.getAxis('bottom').setGrid(20)

            # Gray plots
            pen = pg.mkPen(color=self.__color.lighter(), width=1, style=Qt.DashLine)
            for network in self.__networks:
                vector = network.vector(paramType, n, m)
                if vector is None:
                    continue

                x = network.freq()
                y = np.angle(vector) / np.pi * 180.
                p.plot(x, y, pen=pen)

            # Highlight plots
            pen = None
            for network in self.__networks:
                vector = network.vector(paramType, n, m)
                if vector is None:
                    continue

                x = network.freq()
                y = np.angle(vector) / np.pi * 180.
                pItem = p.plot(x, y, pen=pen, name=network.text())
                self.__hlPlots.append(pItem)

            self.hlPlot()

        #------------------------------------------------------------------------------------------
        # MAG & PHASE PLOT
        #------------------------------------------------------------------------------------------
        elif diagram == Diagrams.MAG_PHASE:
            pMag = self.__graph.addPlot(row=0, col=0)
            pMag.setLabels(bottom='Frequency (Hz)', left='Mag (dB)')
            pMag.getAxis('left').setGrid(20)
            pMag.getAxis('bottom').setGrid(20)

            pPhi = self.__graph.addPlot(row=1, col=0)
            pPhi.setLabels(bottom='Frequency (Hz)', left='Phase (deg)')
            pPhi.getAxis('left').setGrid(20)
            pPhi.getAxis('bottom').setGrid(20)

            pMag.getAxis('left').setWidth(50)
            pPhi.getAxis('left').setWidth(50)
            pPhi.setXLink(pMag)

            # Gray plots
            pen = pg.mkPen(color=self.__color.lighter(), width=1, style=Qt.DashLine)
            for network in self.__networks:
                vector = network.vector(paramType, n, m)
                if vector is None:
                    continue

                x = network.freq()
                y1 = 20. * np.log10(np.abs(vector))
                y2 = np.angle(vector) / np.pi * 180.

                pMag.plot(x, y1, pen=pen)
                pPhi.plot(x, y2, pen=pen)

            # Highlight plots
            pen = None
            for network in self.__networks:
                vector = network.vector(paramType, n, m)
                if vector is None:
                    continue

                x = network.freq()
                y1 = 20. * np.log10(np.abs(vector))
                y2 = np.angle(vector) / np.pi * 180.

                pItem1 = pMag.plot(x, y1, pen=pen, name=network.text())
                pItem2 = pPhi.plot(x, y2, pen=pen, name=network.text())
                self.__hlPlots.append(pItem1)
                self.__hlPlots.append(pItem2)

            self.hlPlot()

        #------------------------------------------------------------------------------------------
        # REAL PLOT
        #------------------------------------------------------------------------------------------
        elif diagram == Diagrams.REAL:
            p = self.__graph.addPlot()
            p.setLabels(bottom='Frequency (Hz)', left='Re, '+paramType.value)
            p.getAxis('left').setGrid(20)
            p.getAxis('bottom').setGrid(20)

            # Gray plots
            pen = pg.mkPen(color=self.__color.lighter(), width=1, style=Qt.DashLine)
            for network in self.__networks:
                vector = network.vector(paramType, n, m)
                if vector is None:
                    continue

                x = network.freq()
                y = np.real(vector)
                p.plot(x, y, pen=pen)

            # Highlight plots
            pen = None
            for network in self.__networks:
                vector = network.vector(paramType, n, m)
                if vector is None:
                    continue

                x = network.freq()
                y = np.real(vector)
                pItem = p.plot(x, y, pen=pen, name=network.text())
                self.__hlPlots.append(pItem)

            self.hlPlot()

        #------------------------------------------------------------------------------------------
        # IMAGINARY PLOT
        #------------------------------------------------------------------------------------------
        elif diagram == Diagrams.IMAGINARY:
            p = self.__graph.addPlot()
            p.setLabels(bottom='Frequency (Hz)', left='Im, '+paramType.value)
            p.getAxis('left').setGrid(20)
            p.getAxis('bottom').setGrid(20)

            # Gray plots
            pen = pg.mkPen(color=self.__color.lighter(), width=1, style=Qt.DashLine)
            for network in self.__networks:
                vector = network.vector(paramType, n, m)
                if vector is None:
                    continue

                x = network.freq()
                y = np.imag(vector)
                p.plot(x, y, pen=pen)

            # Highlight plots
            pen = None
            for network in self.__networks:
                vector = network.vector(paramType, n, m)
                if vector is None:
                    continue

                x = network.freq()
                y = np.imag(vector)
                pItem = p.plot(x, y, pen=pen, name=network.text())
                self.__hlPlots.append(pItem)

            self.hlPlot()

        #------------------------------------------------------------------------------------------
        # REAL & IMAGINARY PLOT
        #------------------------------------------------------------------------------------------
        elif diagram == Diagrams.REAL_IMAGINARY:
            pRe = self.__graph.addPlot(row=0, col=0)
            pRe.setLabels(bottom='Frequency (Hz)', left='Re')
            pRe.getAxis('left').setGrid(20)
            pRe.getAxis('bottom').setGrid(20)

            pIm = self.__graph.addPlot(row=1, col=0)
            pIm.setLabels(bottom='Frequency (Hz)', left='Im')
            pIm.getAxis('left').setGrid(20)
            pIm.getAxis('bottom').setGrid(20)

            pRe.getAxis('left').setWidth(50)
            pIm.getAxis('left').setWidth(50)
            pIm.setXLink(pRe)

            # Gray plots
            pen = pg.mkPen(color=self.__color.lighter(), width=1, style=Qt.DashLine)
            for network in self.__networks:
                vector = network.vector(paramType, n, m)
                if vector is None:
                    continue

                x = network.freq()
                y1 = np.real(vector)
                y2 = np.imag(vector)

                pRe.plot(x, y1, pen=pen)
                pIm.plot(x, y2, pen=pen)

            # Highlight plots
            pen = None
            for network in self.__networks:
                vector = network.vector(paramType, n, m)
                if vector is None:
                    continue

                x = network.freq()
                y1 = np.real(vector)
                y2 = np.imag(vector)

                pItem1 = pRe.plot(x, y1, pen=pen, name=network.text())
                pItem2 = pIm.plot(x, y2, pen=pen, name=network.text())
                self.__hlPlots.append(pItem1)
                self.__hlPlots.append(pItem2)

            self.hlPlot()

        #------------------------------------------------------------------------------------------
        # SMITH PLOT
        #------------------------------------------------------------------------------------------
        elif diagram == Diagrams.SMITH:
            p = self.__graph.addPlot()

            # Lock aspect ratio
            p.setAspectLocked(True)
            pen = pg.mkPen(color='#808080', width=1, style=Qt.SolidLine)
            
            # Constant resistance curves
            for ReZ in [0., .2, .5, 1., 2., 5., 10.]:
                t = np.linspace(0, 2 * np.pi, 256)
                center = ReZ / (ReZ + 1)
                radius = 1 / (ReZ + 1)
                p.plot(center + radius * np.cos(t), radius * np.sin(t), pen=pen)

            # Constant reactance curves
            for ImZ in [.2, .5, 1., 2., 5.]:
                Zc = 1j * ImZ
                radius = 1 / ImZ
                angle = np.mod(np.angle((1 / Zc - 1) / (Zc + 1)), 2 * np.pi)
                t = np.linspace(angle, 3 * np.pi / 2, 256)
                p.plot(1 + radius * np.cos(t),  radius + radius * np.sin(t), pen=pen)
                p.plot(1 + radius * np.cos(t), -radius - radius * np.sin(t), pen=pen)

            p.getAxis('left').setGrid(20)
            p.getAxis('bottom').setGrid(20)
            p.setLabels(bottom='Real', left='Imaginary')

            # Gray plots
            pen = pg.mkPen(color=self.__color.lighter(), width=1, style=Qt.DashLine)
            for network in self.__networks:
                vector = network.vector(paramType, n, m)
                if vector is None:
                    continue

                x = np.real(vector)
                y = np.imag(vector)
                p.plot(x, y, pen=pen)

            # Highlight plots
            pen = None
            for network in self.__networks:
                vector = network.vector(paramType, n, m)
                if vector is None:
                    continue

                x = np.real(vector)
                y = np.imag(vector)
                pItem = p.plot(x, y, pen=pen, name=network.text())
                self.__hlPlots.append(pItem)

            self.hlPlot()

        #------------------------------------------------------------------------------------------
        # ADMITTANCE SMITH PLOT
        #------------------------------------------------------------------------------------------
        elif diagram == Diagrams.ADMITTANCE_SMITH:
            p = self.__graph.addPlot()

            # Lock aspect ratio
            p.setAspectLocked(True)
            pen = pg.mkPen(color='#808080', width=1, style=Qt.SolidLine)
            
            # Constant conductance curves
            for ReY in [0., .2, .5, 1., 2., 5., 10.]:
                t = np.linspace(0, 2 * np.pi, 256)
                center = -ReY / (ReY + 1)
                radius = 1 / (ReY + 1)
                p.plot(center + radius * np.cos(t), radius * np.sin(t), pen=pen)

            # Constant susceptance curves
            for ImY in [.2, .5, 1., 2., 5.]:
                Yc = 1j * ImY
                radius = 1 / ImY
                angle = np.mod(np.angle((1 / Yc - 1) / (Yc + 1)), 2 * np.pi)
                t = np.linspace(angle, 3 * np.pi / 2, 256)
                p.plot(-1 - radius * np.cos(t),  radius + radius * np.sin(t), pen=pen)
                p.plot(-1 - radius * np.cos(t), -radius - radius * np.sin(t), pen=pen)

            p.getAxis('left').setGrid(20)
            p.getAxis('bottom').setGrid(20)
            p.setLabels(bottom='Real', left='Imaginary')

            # Gray plots
            pen = pg.mkPen(color=self.__color.lighter(), width=1, style=Qt.DashLine)
            for network in self.__networks:
                vector = network.vector(paramType, n, m)
                if vector is None:
                    continue

                x = np.real(vector)
                y = np.imag(vector)
                p.plot(x, y, pen=pen)

            # Highlight plots
            pen = None
            for network in self.__networks:
                vector = network.vector(paramType, n, m)
                if vector is None:
                    continue

                x = np.real(vector)
                y = np.imag(vector)
                pItem = p.plot(x, y, pen=pen, name=network.text())
                self.__hlPlots.append(pItem)

            self.hlPlot()

        #------------------------------------------------------------------------------------------
        # POLAR PLOT
        #------------------------------------------------------------------------------------------
        elif diagram == Diagrams.POLAR:
            p = self.__graph.addPlot()

            # Lock aspect ratio
            p.setAspectLocked(True)
            pen = pg.mkPen(color='#808080', width=1, style=Qt.SolidLine)

            # Theta-curves
            step = 30
            for i in range(int(360 / step)):
                theta = step * i / 180. * np.pi
                p.plot([0, np.cos(theta)], [0, np.sin(theta)], pen=pen)

            # R-curves
            for r in [0.25, 0.5, 0.75, 1.]:
                t = np.linspace(0, 2 * np.pi, 361)
                p.plot(r * np.cos(t), r * np.sin(t), pen=pen)

            p.getAxis('left').setGrid(20)
            p.getAxis('bottom').setGrid(20)
            p.setLabels(bottom='Real', left='Imaginary')

            # Gray plots
            pen = pg.mkPen(color=self.__color.lighter(), width=1, style=Qt.DashLine)
            for network in self.__networks:
                vector = network.vector(paramType, n, m)
                if vector is None:
                    continue

                x = np.real(vector)
                y = np.imag(vector)
                p.plot(x, y, pen=pen)

            # Highlight plots
            pen = None
            for network in self.__networks:
                vector = network.vector(paramType, n, m)
                if vector is None:
                    continue

                x = np.real(vector)
                y = np.imag(vector)
                pItem = p.plot(x, y, pen=pen, name=network.text())
                self.__hlPlots.append(pItem)

            self.hlPlot()

