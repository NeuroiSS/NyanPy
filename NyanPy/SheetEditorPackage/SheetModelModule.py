from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
from numpy import *
import re

from SheetCmdsModule import SetCmd

class SheetModel(QtCore.QAbstractTableModel):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.__data = {}
        self.__rows = 100
        self.__cols = 100
        self.__numStr = '{:g}'
        self.__undoStack = QtGui.QUndoStack()

    def clear(self):
        self.__data = {}
        self.__rows = 100
        self.__cols = 100
        self.__numStr = '{:g}'

        self.layoutChanged.emit()

    def indices(self) -> list:
        return [self.index(row, col) for (row, col) in self.__data]

    def countRows(self) -> int:
        rows = [row for (row, col) in self.__data]
        return max(rows) + 1 if rows else 0

    def countCols(self) -> int:
        cols = [col for (row, col) in self.__data]
        return max(cols) + 1 if cols else 0

    def undoStack(self) -> QtGui.QUndoStack:
        return self.__undoStack

    def numStr(self) -> str:
        return self.__numStr

    def setNumStr(self, numStr:str):
        self.__numStr = numStr
        self.layoutChanged.emit()

    @staticmethod
    def split(text:str) -> list:
        isQuote = False
        doubleQuote = '"'
        delimiter = ','
        items = []
        item = ''
        for c in text:
            if isQuote:
                item += c
                isQuote = (c != doubleQuote)
            else:
                if c == delimiter:
                    items += [item.strip('"\r\n ')]
                    item = ''
                else:
                    item += c
                    isQuote = (c == doubleQuote)
        items += [item.strip('"\r\n ')]
        return items

    def load(self, path:str, fileType = 'CSV'):
        self.__data = {}
        row = 0
        with open(path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                items = self.split(line) if fileType == 'CSV' else line.split()
                for col, item in enumerate(items):
                    self.__data[row, col] = self.__convert(item)
                row += 1
        self.__rows = max(100, self.countRows())
        self.__cols = max(100, self.countCols())
        self.layoutChanged.emit()

    def write(self, path:str):
        rowCount = self.countRows()
        numTypes = [float, complex, float32, float64, complex64, complex128]
        text = ''
        delimiter = ','
        for row in range(rowCount):
            cols = [col_ for (row_, col_) in self.__data if row_ == row]
            colCount = max(cols) + 1 if cols else 0
            for col in range(colCount):
                item = self.__data.get((row, col))
                text += delimiter if col != 0 else ''
                if item is not None:
                    text += '"'+item+'"' if type(item) is str and delimiter in item\
                            else item if type(item) is str\
                            else '{:.14e}'.format(item) if type(item) in numTypes\
                            else str(item)
            text += '\n'
        with open(path, 'w') as f:
            f.write(text)

    def __convert(self, s):
        if type(s) is str:
            try:
                return int(s)
            except ValueError:
                try:
                    return float(s)
                except ValueError:
                    try:
                        return complex(s)
                    except ValueError:
                        pass
        return s

    @override
    def rowCount(self, parent:QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return self.__rows if not parent.isValid() else 0

    @override
    def columnCount(self, parent:QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return self.__cols if not parent.isValid() else 0

    @override
    def headerData(self, section:int, orientation:Qt.Orientation, role:int = Qt.DisplayRole):
        return section + 1 if role == Qt.DisplayRole else None

    @override
    def flags(self, index:QtCore.QModelIndex) -> Qt.ItemFlags:
        return Qt.ItemIsEditable | super().flags(index) if index.isValid()\
                else Qt.NoItemFlags
    
    @override
    def data(self, index:QtCore.QModelIndex, role:int = Qt.UserRole):
        if not index.isValid():
            return None
        numStr = self.__numStr
        numTypes = [float, complex, float32, float64, complex64, complex128]
        apostrophe = '\''
        item = self.__data.get((index.row(), index.column()))
        if role == Qt.UserRole:
            return item
        if role == Qt.EditRole:
            return item if item is None or type(item) is str\
                    else numStr.format(item) if type(item) in numTypes\
                    else str(item)
        if role == Qt.DisplayRole:
            return item if item is None\
                    else '""' if item == ''\
                    else item[1:] if type(item) is str and item[0] == apostrophe\
                    else item[0:] if type(item) is str\
                    else numStr.format(item) if type(item) in numTypes\
                    else str(item)
        return None

    @override
    def setData(self, index:QtCore.QModelIndex, value, role:int = Qt.UserRole) -> bool:
        row = index.row()
        col = index.column()
        if role == Qt.EditRole:
            indices = [index]
            vals = [value]
            self.__undoStack.push(SetCmd(self, indices, vals))
            self.dataChanged.emit(index, index, [Qt.EditRole])
            return True
        if role == Qt.UserRole:
            if value is None:
                if (row, col) in self.__data:
                    self.__data.pop((row, col))
                    self.dataChanged.emit(index, index, [Qt.UserRole])
                    return True
                else:
                    return False
            else:
                self.__data[row, col] = self.__convert(value)
                self.dataChanged.emit(index, index, [Qt.UserRole])
                return True
        return False

    @override
    def insertRows(self, pos:int, cnt:int, parent = QtCore.QModelIndex()) -> bool:
        self.beginInsertRows(parent, pos, pos + cnt - 1)
        tmp = {}
        for (row, col) in list(self.__data):
            if row >= pos:
                tmp[row, col] = self.__data.pop((row, col))
        for (row, col) in tmp:
            self.__data[row + cnt, col] = tmp[row, col]
        self.__rows += cnt
        self.endInsertRows()
        return True

    @override
    def insertColumns(self, pos:int, cnt:int, parent = QtCore.QModelIndex()) -> bool:
        self.beginInsertColumns(parent, pos, pos + cnt - 1)
        tmp = {}
        for (row, col) in list(self.__data):
            if col >= pos:
                tmp[row, col] = self.__data.pop((row, col))
        for (row, col) in tmp:
            self.__data[row, col + cnt] = tmp[row, col]
        self.__cols += cnt
        self.endInsertColumns()
        return True

    @override
    def removeRows(self, pos:int, cnt:int, parent = QtCore.QModelIndex()) -> bool:
        self.beginRemoveRows(parent, pos, pos + cnt - 1)
        tmp = {}
        for (row, col) in list(self.__data):
            if row >= pos + cnt:
                tmp[row, col] = self.__data.pop((row, col))
        for (row, col) in tmp:
            self.__data[row - cnt, col] = tmp[row, col]
        self.__rows -= cnt
        self.endRemoveRows()
        return True

    @override
    def removeColumns(self, pos:int, cnt:int, parent = QtCore.QModelIndex()) -> bool:
        self.beginRemoveColumns(parent, pos, pos + cnt - 1)
        tmp = {}
        for (row, col) in list(self.__data):
            if col >= pos + cnt:
                tmp[row, col] = self.__data.pop((row, col))
        for (row, col) in tmp:
            self.__data[row, col - cnt] = tmp[row, col]
        self.__cols -= cnt
        self.endRemoveColumns()
        return True

