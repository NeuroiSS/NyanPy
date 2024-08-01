from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys
import os

from SheetWidgetModule import SheetWidget
from VariablesPackage.VariablesWidgetModule import VariablesWidget
from PlottingPackage.PlottingWidgetModule import PlottingWidget

class SheetEditor(QtWidgets.QMainWindow):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.__sheetWidget = SheetWidget()
        self.__sheetView = self.__sheetWidget.sheetView()
        self.__variablesWidget = VariablesWidget()
        self.__plottingWidget = PlottingWidget()
        self.__dock1 = QtWidgets.QDockWidget('Sheet')
        self.__dock2 = QtWidgets.QDockWidget('Variables')
        self.__dock3 = QtWidgets.QDockWidget('Plotting')

        # Link variables
        self.__variablesWidget.setList(self.__sheetView.list())

        self.setupUi()
        self.connectSignals()

    @Slot()
    def receiveCommand(self, commandText:str):
        # Focus to SheetView
        self.__sheetView.setFocus()

        # Interpret command
        commandText = commandText.strip()
        if not commandText:
            pass
        elif commandText in ['e', 'open']:
            self.__sheetView.open()
        elif commandText in ['w', 'write', 'save']:
            self.__sheetView.save()
        elif commandText in ['n', 'new']:
            self.__sheetView.new()
        elif commandText in ['s', 'find', 'replace']:
            self.__sheetView.findReplace()
        elif commandText in ['q', 'quit', 'exit']:
            self.close()
        else:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText('Sorry, could not interpret the command')
            msgbox.exec()

    @Slot()
    def receiveDataListItems(self, items):
        self.__plottingWidget.receiveDataListItems(items)

    @Slot()
    def about(self):
        text = '''
        <h1><strong>SheetEditor</strong></h1>
        Spreadsheet for Vimmers.<br>

        <br><strong>Features</strong><br>
        - Moving cursor with HJKL keys like Vim<br>
        - Switching editor modes like Vim<br>
        - Variables for calculations<br>
        - Interactive graph plotting based on PyQtGraph<br>

        <br><strong>Modes</strong><br>
        - NORMAL mode [Esc] - Default mode<br>
        - INSERT mode [I] - Insert/remove lines in the selected range by HJKL<br>
        - INSERT-LINE mode [Shift+I] - Insert/remove lines by HJKL<br>
        - VISUAL mode [V] - Select cells by HJKL<br>
        - VISUAL-LINE mode [Shift+V] - Select lines by HJKL<br>

        <br><strong>Variables</strong><br>
        Press [S] to assign the selected data to a variable. Variables can also be
        defined with Python expressions. NumPy functions are available. Press [P] to
        put the evaluated results into the spreadsheet.<br>

        <br><strong>Plotting Graphs</strong><br>
        Press [A] to add the selected data to the plotting list. In the 'Plotting'
        dock window (or tab), you can modify the styles and make graphs.<br>

        <br><strong>Shortcuts</strong><br>
        [Ctrl+C] or [Y]:copy (yank), [Ctrl+V] or [P]:paste (put), [Del]:delete,
        [Ctrl+X] or [D]:cut (delete), [Ctrl+F]:find & replace, [Ctrl+Z] or [U]:undo,
        [Ctrl+Y] or [Ctrl+R] (redo), [Ctrl+N]:new, [Ctrl+O]:open, [Ctrl+S]:save,
        [Ctrl+Shift+S]:save as, [Esc] or [Ctrl+[]:NORMAL mode, [I]:INSERT mode,
        [Shift+I]:INSERT-LINE mode, [V]:VISUAL mode, [Shift+V]:VISUAL-LINE mode,
        [E]:scientific format, [F]:fixed-point format, [G]:general format,
        [S]:set variable, [Shift+P]:put variable, [A]:add to plotting list<br>
        
        <br><strong>Commands</strong><br>
        [:e] or [:open]:open, [:w] or [:write] or [:save]:save, [:n] or [:new]:new,
        [:s] or [:find] or [:replace]:find & replace,
        [:q] or [:quit] or [:exit]:quit<br>
        '''
        QtWidgets.QMessageBox.about(self, 'About', text)

    def setupUi(self):
        # Menu bar
        menuBar = self.menuBar()
        menu = menuBar.addMenu('Docks')
        menu.addAction(self.__dock1.toggleViewAction())
        menu.addAction(self.__dock2.toggleViewAction())
        menu.addAction(self.__dock3.toggleViewAction())
        menu = menuBar.addMenu('About')
        menu.addAction('SheetEditor', self.about)

        # Dock widgets
        self.__dock1.setWidget(self.__sheetWidget)
        self.__dock2.setWidget(self.__variablesWidget)
        self.__dock3.setWidget(self.__plottingWidget)

        self.addDockWidget(Qt.BottomDockWidgetArea, self.__dock1)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.__dock2)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.__dock3)
        self.tabifyDockWidget(self.__dock1, self.__dock2)
        self.tabifyDockWidget(self.__dock1, self.__dock3)
        self.__dock1.raise_()

    def connectSignals(self):
        self.__sheetWidget.commandEntered.connect(self.receiveCommand)
        self.__sheetView.plottingRequested.connect(self.receiveDataListItems)
        self.__sheetView.windowTitleChanged.connect(self.setWindowTitle)
        self.setWindowTitle(self.__sheetView.windowTitle())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = SheetEditor()
    ex.show()
    sys.exit(app.exec())

