from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys
import os

QtCore.QDir.addSearchPath('img', os.path.join(os.path.dirname(__file__), 'Resources/Images'))

from AnalogClockPackage.AnalogClockModule import AnalogClock
from CodeEditorPackage.CodeEditorWindowModule import CodeEditorWindow
from SheetEditorPackage.SheetEditorModule import SheetEditor

class Launcher(QtWidgets.QMainWindow):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.__children = []

        # TableWidget
        tableWidget = QtWidgets.QTreeWidget()
        tableWidget.setHeaderLabels(['Name', 'Description'])
        tableWidget.setHeaderHidden(True)

        # Add Items to TableWidget
        apps = QtWidgets.QTreeWidgetItem(['Apps'])
        apps.addChild(QtWidgets.QTreeWidgetItem(['AnalogClock', 'Simple analog clock']))
        apps.addChild(QtWidgets.QTreeWidgetItem(['CodeEditor' , 'Text editor for coding Python and Matlab/GNU Octave']))
        apps.addChild(QtWidgets.QTreeWidgetItem(['SheetEditor', 'Vim-like spreadsheet with plotting graphs']))
        tableWidget.addTopLevelItem(apps)

        tableWidget.expandAll()
        tableWidget.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        tableWidget.itemDoubleClicked.connect(self.launchApp)
        self.setCentralWidget(tableWidget)

        # MenuBar
        menuBar = self.menuBar()
        menu = menuBar.addMenu('Widgets')
        menu.addAction('Show all', self.showAll)
        menu.addAction('Close all', self.closeAll)

        # StyleSheet
        try:
            with open(os.path.join(os.path.dirname(__file__), 'Styles/NyanDark.qss'), 'r') as f:
                qss = f.read()
        except Exception:
            qss = ''

        self.setStyleSheet(qss)
        self.setWindowTitle('NyanPy Launcher')
        self.setWindowIcon(QtGui.QIcon('img:nyan.png'))
        self.resize(500, 150)

    @Slot()
    def launchApp(self, item, column):
        name = item.text(0)
        app = AnalogClock() if name == 'AnalogClock'\
                else CodeEditorWindow() if name == 'CodeEditor'\
                else SheetEditor() if name == 'SheetEditor'\
                else None
        if app:
            self.__children.append(app)
            app.setStyleSheet(self.styleSheet())
            app.setWindowIcon(QtGui.QIcon('img:nyanpaw.png'))
            app.show()

    @Slot()
    def showAll(self):
        self.__children = [child for child in self.__children if child.isVisible()]
        for child in self.__children:
            child.raise_()

    @Slot()
    def closeAll(self):
        for child in self.__children:
            child.close()
        self.__children = [child for child in self.__children if child.isVisible()]

    @override
    def closeEvent(self, event):
        self.__children = [child for child in self.__children if child.isVisible()]
        if self.__children:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText('Close all widgets?')
            msgbox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            answer = msgbox.exec()
            if answer == QtWidgets.QMessageBox.No:
                event.ignore()
                return

        self.closeAll()
        event.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Launcher()
    ex.show()
    sys.exit(app.exec())

