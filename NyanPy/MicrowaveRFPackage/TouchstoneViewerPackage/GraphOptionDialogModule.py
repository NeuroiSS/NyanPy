from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys
import os

import pyqtgraph as pg

class GraphOptionDialog(QtWidgets.QDialog):

    optionsChanged = Signal()

    def __init__(self, parent = None):
        super().__init__(parent)
        self.__whiteBackRadioButton = QtWidgets.QRadioButton('White')
        self.__blackBackRadioButton = QtWidgets.QRadioButton('Black')
        self.__antialiasCheckBox = QtWidgets.QCheckBox('Antialias:')

        # Radio group
        self.__buttonGroup = QtWidgets.QButtonGroup()
        self.__buttonGroup.addButton(self.__whiteBackRadioButton)
        self.__buttonGroup.addButton(self.__blackBackRadioButton)

        self.setupUi()
        self.setWindowTitle('Graph Options')

    def setupUi(self):
        self.__whiteBackRadioButton.setChecked(True)
        self.__blackBackRadioButton.setChecked(False)
        self.__antialiasCheckBox.setChecked(True)

        OK = QtWidgets.QDialogButtonBox.Ok
        CANCEL = QtWidgets.QDialogButtonBox.Cancel
        buttonBox = QtWidgets.QDialogButtonBox(OK | CANCEL)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        hboxlayout = QtWidgets.QHBoxLayout()
        hboxlayout.addWidget(self.__whiteBackRadioButton)
        hboxlayout.addWidget(self.__blackBackRadioButton)

        vboxlayout = QtWidgets.QVBoxLayout()
        vboxlayout.addWidget(QtWidgets.QLabel('Background:'))
        vboxlayout.addLayout(hboxlayout)
        vboxlayout.addWidget(self.__antialiasCheckBox)
        vboxlayout.addWidget(buttonBox)

        self.setLayout(vboxlayout)

    @override
    def accept(self):
        rb = self.__buttonGroup.checkedButton()
        background = 'w' if rb.text() == 'White' else 'k'
        foreground = 'k' if rb.text() == 'White' else 'd'
        antialias = self.__antialiasCheckBox.isChecked()

        # PyQtGraph Global Options
        pg.setConfigOptions(antialias=antialias, background=background, foreground=foreground)
        self.optionsChanged.emit()

        super().accept()

