from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys
import os

from DataPropertiesWidgetModule import DataPropertiesWidget
from GraphPropertiesWidgetModule import GraphPropertiesWidget
from PlotModule import Plot

class PlottingWidget(QtWidgets.QWidget):

    def __init__(self, parent = None):
        super().__init__(parent)
        # Plots (Graphics Layout Widgets)
        self.__plots = []

        # UIs
        self.__dataPropWidget = DataPropertiesWidget()
        self.__graphPropWidget = GraphPropertiesWidget()
        self.__pushButton_Import = QtWidgets.QPushButton('Import')
        self.__pushButton_Export = QtWidgets.QPushButton('Export')
        self.__pushButton_Plot = QtWidgets.QPushButton('Plot')
        self.__pushButton_Replot = QtWidgets.QPushButton('Replot')

        self.setupUi()
        self.connectSignals()

    @Slot()
    def receiveDataListItems(self, items):
        self.__dataPropWidget.receiveDataListItems(items)

    @Slot()
    def plot(self):
        plot = Plot(self)
        plot.plot(self.__dataPropWidget.listItems(), self.__dataPropWidget.colorOrder(), 
                self.__graphPropWidget.graphProperties())

        self.__plots = [p for p in self.__plots if p.isVisible()]
        self.__plots.append(plot)
        plot.show()

    @Slot()
    def replot(self):
        self.__plots = [p for p in self.__plots if p.isVisible()]
        if not self.__plots:
            return

        plot = self.__plots[-1]
        plot.plot(self.__dataPropWidget.listItems(), self.__dataPropWidget.colorOrder(), 
                self.__graphPropWidget.graphProperties())

    @Slot()
    def import_(self):
        msgbox = QtWidgets.QMessageBox(self)
        msgbox.setText('Sorry, not implemented yet.')
        msgbox.exec()

    @Slot()
    def export(self):
        msgbox = QtWidgets.QMessageBox(self)
        msgbox.setText('Sorry, not implemented yet.')
        msgbox.exec()

    def setupUi(self):
        tabWidget = QtWidgets.QTabWidget()
        tabWidget.addTab(self.__dataPropWidget, 'Data Properties')
        tabWidget.addTab(self.__graphPropWidget, 'Graph Properties')

        hboxlayout = QtWidgets.QHBoxLayout()
        hboxlayout.addStretch()
        hboxlayout.addWidget(self.__pushButton_Import)
        hboxlayout.addWidget(self.__pushButton_Export)
        hboxlayout.addWidget(self.__pushButton_Plot)
        hboxlayout.addWidget(self.__pushButton_Replot)

        vboxlayout = QtWidgets.QVBoxLayout()
        vboxlayout.addWidget(tabWidget)
        vboxlayout.addLayout(hboxlayout)
        self.setLayout(vboxlayout)

    def connectSignals(self):
        self.__pushButton_Import.clicked.connect(self.import_)
        self.__pushButton_Export.clicked.connect(self.export)
        self.__pushButton_Plot.clicked.connect(self.plot)
        self.__pushButton_Replot.clicked.connect(self.replot)

        self.__dataPropWidget.valueUpdated.connect(self.replot)
        self.__graphPropWidget.valueUpdated.connect(self.replot)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = PlottingWidget()
    ex.show()
    sys.exit(app.exec())

