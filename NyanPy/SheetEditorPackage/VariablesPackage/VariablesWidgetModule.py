from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys
import os

from VariableItemListModule import VariableItemList
from VariableTableModelModule import VariableTableModel

class VariablesWidget(QtWidgets.QWidget):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.__list = VariableItemList()
        self.__model = VariableTableModel(self.__list)
        self.__table = QtWidgets.QTableView()
        self.__table.setModel(self.__model)

        self.setupTable()
        self.setupUi()
        self.setWindowTitle('Variables')

    def setList(self, list_:VariableItemList):
        self.__list = list_
        self.__model = VariableTableModel(self.__list)
        self.__table.setModel(self.__model)

    def select(self, row:int):
        index = self.__model.index(row, 0)
        if index.isValid():
            self.__table.setCurrentIndex(index)

    def __add_y(self, n = 1):
        name = 'y{:d}'.format(n)
        if name in self.__list.names():
            self.__add_y(n + 1)
            return
        row = self.__list.append(name, 0)
        self.select(row)

    @Slot()
    def add(self):
        self.__add_y(1)

    @Slot()
    def remove(self):
        selected = self.__table.selectedIndexes()
        if not selected:
            return
        row = selected[0].row()
        self.__list.pop(row)
        if row == self.__list.count():
            self.select(row - 1)

    @Slot()
    def moveUp(self):
        selected = self.__table.selectedIndexes()
        if not selected:
            return
        row = selected[0].row()
        if row != 0:
            self.__list.swap(row - 1, row)
            self.select(row - 1)

    @Slot()
    def moveDown(self):
        selected = self.__table.selectedIndexes()
        if not selected:
            return
        row = selected[0].row()
        if row != self.__list.count() - 1:
            self.__list.swap(row, row + 1)
            self.select(row + 1)

    @Slot()
    def importXml(self):
        path, selectedFilter = QtWidgets.QFileDialog.getOpenFileName(self,\
                'Import XML', '', 'XML Files (*.xml)')
        if not path:
            return
        try:
            self.__list.importXml(path)
        except Exception as e:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText(str(e))
            msgbox.exec()

    @Slot()
    def exportXml(self):
        path, selectedFilter = QtWidgets.QFileDialog.getSaveFileName(self,\
                'Export XML', '', 'XML Files (*.xml)')
        if not path:
            return
        try:
            self.__list.exportXml(path)
        except Exception as e:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText(str(e))
            msgbox.exec()

    def __createButton(self, text, receiver) -> QtWidgets.QPushButton:
        button = QtWidgets.QPushButton()
        button.setText(text)
        button.clicked.connect(receiver)
        return button

    def setupTable(self):
        table = self.__table
        columnWidths = [100, 150, 150, 100, 250]

        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        table.verticalHeader().setDefaultSectionSize(20)
        table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

        horizontalHeader = self.__table.horizontalHeader()
        for section, width in enumerate(columnWidths):
            horizontalHeader.resizeSection(section, width)

    @Slot()
    def setupUi(self):
        button_Add    = self.__createButton('Add', self.add)
        button_Remove = self.__createButton('Remove', self.remove)
        button_Up     = self.__createButton('Up', self.moveUp)
        button_Down   = self.__createButton('Down', self.moveDown)
        button_Import = self.__createButton('Import', self.importXml)
        button_Export = self.__createButton('Export', self.exportXml)

        hboxlayout = QtWidgets.QHBoxLayout()
        hboxlayout.addWidget(button_Add)
        hboxlayout.addWidget(button_Remove)
        hboxlayout.addWidget(button_Up)
        hboxlayout.addWidget(button_Down)
        hboxlayout.addWidget(button_Import)
        hboxlayout.addWidget(button_Export)
        hboxlayout.addStretch()

        vboxlayout = QtWidgets.QVBoxLayout()
        vboxlayout.addWidget(self.__table)
        vboxlayout.addLayout(hboxlayout)
        self.setLayout(vboxlayout)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = VariablesWidget()
    ex.show()
    sys.exit(app.exec())

