from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys
import os

from SheetViewModule import SheetView, Modes
from SheetStatusBarModule import SheetStatusBar

class SheetWidget(QtWidgets.QWidget):

    # Signals
    commandEntered = Signal(str)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.__sheetView = SheetView()
        self.__statusBar = SheetStatusBar()
        self.setupUi()
        self.connectSignals()

    def sheetView(self):
        return self.__sheetView

    def setupUi(self):
        vboxlayout = QtWidgets.QVBoxLayout(self)
        vboxlayout.addWidget(self.__sheetView)
        vboxlayout.addWidget(self.__statusBar)
        vboxlayout.setSpacing(0)
        vboxlayout.setContentsMargins(0, 0, 0, 0)
        self.setWindowTitle(self.__sheetView.windowTitle())

    def connectSignals(self):
        self.__sheetView.modeChanged.connect(self.__statusBar.receiveMode)
        self.__sheetView.commandRequested.connect(self.__statusBar.enterInputMode)
        self.__sheetView.windowTitleChanged.connect(self.setWindowTitle)
        self.__statusBar.commandEntered.connect(self.commandEntered.emit)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = SheetWidget()
    ex.show()
    sys.exit(app.exec())

