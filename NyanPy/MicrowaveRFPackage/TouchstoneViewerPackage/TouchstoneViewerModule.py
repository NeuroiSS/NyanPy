from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys
import os
import numpy as np

from NetworkParameterModule import NetworkParameter
from NetworkParameterPlotModule import NetworkParameterPlot
from GraphOptionDialogModule import GraphOptionDialog

class TouchstoneViewer(QtWidgets.QMainWindow):

    # Signals
    plotRequested = Signal()

    MAX_ROW_COUNT = 3
    MAX_COLUMN_COUNT = 3

    def __init__(self, parent = None):
        super().__init__(parent)
        self.__rowCount = 2
        self.__columnCount = 2
        self.__filesComboBox = QtWidgets.QComboBox()
        self.__filesComboBox.setMinimumWidth(350)
        self.__addButton = QtWidgets.QPushButton('Add')
        self.__clearButton = QtWidgets.QPushButton('Clear')
        self.__mainLayout = QtWidgets.QGridLayout()
        self.__mainLayout.setContentsMargins(0, 0, 0, 0)
        self.__mainLayout.setSpacing(0)
        self.__rowMenu = QtWidgets.QMenu('Row', self)
        self.__columnMenu = QtWidgets.QMenu('Column', self)
        self.__graphOptionDialog = GraphOptionDialog(self)
        self.__networks = []

        self.setupUi()
        self.updateUi()
        self.connectSignals()
        self.setWindowTitle('TouchstoneViewer')

    @Slot()
    def setRow(self, row:int):
        self.__rowCount = row
        self.updateUi()

    @Slot()
    def setColumn(self, column:int):
        self.__columnCount = column
        self.updateUi()

    @Slot()
    def add(self):
        paths, selectedFilter = QtWidgets.QFileDialog.getOpenFileNames(self,\
                'Open Files', '', 'Touchstone Files (*.s*p)')
        
        # Progress dialog
        progress = QtWidgets.QProgressDialog(self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setLabelText('Loading files...')
        progress.setMaximum(len(paths))
        progress.setCancelButton(None)
        progress.setWindowTitle('Progress')
        progress.show()
        error = ''

        for i, path in enumerate(paths):
            progress.setValue(i)
            QtWidgets.QApplication.processEvents()
            network = NetworkParameter()
            try:
                network.load(path)
            except Exception as e:
                error += 'Loading: '+path+'\nError: '+str(e)+'\n\n'
            else:
                cb = self.__filesComboBox
                texts = [cb.itemText(index) for index in range(cb.count())]
                if network.text() in texts:
                    index = texts.index(network.text())
                    self.__networks[index] = network
                else:
                    self.__networks.append(network)
                    cb.addItem(network.text())

        # Close progress
        progress.close()

        # Error messages
        if error:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText(error)
            msgbox.exec()
        
        # Update plots
        self.plotRequested.emit()

    @Slot()
    def clear(self):
        self.__networks.clear()
        self.__filesComboBox.clear()

        # Update plots
        self.plotRequested.emit()

    def updateUi(self):
        for row in range(self.MAX_ROW_COUNT):
            for column in range(self.MAX_COLUMN_COUNT):
                layoutItem = self.__mainLayout.itemAtPosition(row, column)
                plot = layoutItem.widget()
                if row < self.__rowCount and column < self.__columnCount:
                    plot.show()
                else:
                    plot.hide()

        # Update actions
        for action in self.__rowMenu.actions():
            action.setChecked(action.text() == str(self.__rowCount))
        for action in self.__columnMenu.actions():
            action.setChecked(action.text() == str(self.__columnCount))

        # Resize window
        timer = QtCore.QTimer(self)
        timer.singleShot(50, lambda: self.resize(0, 0))

    def setupUi(self):
        centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(centralWidget)
        colors = '#0072bd #d95319 #edb120 #7e2f8e #77ac30 #4dbeee #a2142f #ffd60a #6582fd #ff453a #00a3a3 #cb845d'
        colors = colors.split()
        colorIndex = 0

        for row in range(self.MAX_ROW_COUNT):
            for column in range(self.MAX_COLUMN_COUNT):
                plot = NetworkParameterPlot(self.__networks)
                plot.setColor(colors[colorIndex])
                plot.setSuffix(str(row + 1) + str(column + 1))
                plot.plot()
                colorIndex = (colorIndex + 1) % len(colors)
                self.__mainLayout.addWidget(plot, row, column)

                # Signal connections
                self.__filesComboBox.currentTextChanged.connect(plot.setCurrentText)
                self.plotRequested.connect(plot.plot)

        # Layouts
        hboxlayout = QtWidgets.QHBoxLayout()
        hboxlayout.addWidget(QtWidgets.QLabel('Files:'))
        hboxlayout.addWidget(self.__filesComboBox)
        hboxlayout.addWidget(self.__addButton)
        hboxlayout.addWidget(self.__clearButton)
        hboxlayout.addStretch()
        hboxlayout.setContentsMargins(5, 5, 5, 5)
        hboxlayout.setSpacing(5)

        vboxlayout = QtWidgets.QVBoxLayout(centralWidget)
        vboxlayout.addLayout(hboxlayout)
        vboxlayout.addLayout(self.__mainLayout)
        vboxlayout.setContentsMargins(0, 0, 0, 0)
        vboxlayout.setSpacing(0)

        # Menu bar
        menuBar = self.menuBar()
        menuBar.addMenu(self.__rowMenu)
        menuBar.addMenu(self.__columnMenu)

        # Row menu
        for row in range(1, self.MAX_ROW_COUNT + 1):
            action = QtGui.QAction(str(row), self)
            action.setCheckable(True)
            action.triggered.connect(lambda state, row=row: self.setRow(row))
            self.__rowMenu.addAction(action)

        # Column menu
        for column in range(1, self.MAX_COLUMN_COUNT + 1):
            action = QtGui.QAction(str(column), self)
            action.setCheckable(True)
            action.triggered.connect(lambda state, column=column: self.setColumn(column))
            self.__columnMenu.addAction(action)

        # Options menu
        menu = menuBar.addMenu('Options')
        menu.addAction('Graph Options', self.__graphOptionDialog.exec)

    def connectSignals(self):
        self.__addButton.clicked.connect(self.add)
        self.__clearButton.clicked.connect(self.clear)
        self.__graphOptionDialog.optionsChanged.connect(lambda: self.plotRequested.emit())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = TouchstoneViewer()
    ex.show()

    QtCore.QDir.addSearchPath('img', '../../Resources/Images')
    with open('../../Styles/NyanDark.qss', 'r') as f:
        ex.setStyleSheet(f.read())

    sys.exit(app.exec())

