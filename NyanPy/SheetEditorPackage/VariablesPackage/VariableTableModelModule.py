from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override

class VariableTableModel(QtCore.QAbstractTableModel):

    def __init__(self, list_, parent = None):
        super().__init__(parent)
        self.__list = list_
        self.__list.eval()
        self.__list.valueChanged.connect(self.update)
        self.__headerTexts = ['Name', 'Value', 'Evaluated Value', 'Type', 'Description']

    @Slot()
    def update(self):
        self.__list.eval()
        self.layoutChanged.emit()

    @override
    def rowCount(self, parent:QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return self.__list.count()

    @override
    def columnCount(self, parent:QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self.__headerTexts)

    @override
    def headerData(self, section:int, orientation:Qt.Orientation, role:int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal and section < len(self.__headerTexts):
                return self.__headerTexts[section]
            if orientation == Qt.Vertical:
                return section + 1
        return None

    @override
    def flags(self, index:QtCore.QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        if self.__headerTexts[index.column()] in ['Name', 'Value', 'Description']:
            return Qt.ItemIsEditable | super().flags(index)
        return super().flags(index)

    @override
    def data(self, index:QtCore.QModelIndex, role:int = Qt.DisplayRole):
        item = self.__list.at(index.row())
        header = self.__headerTexts[index.column()]
        if role in [Qt.DisplayRole, Qt.EditRole]:
            return item.name() if header == 'Name'\
                    else str(item.value()) if header == 'Value'\
                    else str(item.evalValue()) if header == 'Evaluated Value'\
                    else item.evalType() if header == 'Type'\
                    else item.description() if header == 'Description'\
                    else None
        return None

    @override
    def setData(self, index:QtCore.QModelIndex, value, role:int = Qt.EditRole) -> bool:
        if role != Qt.EditRole:
            return False
        item = self.__list.at(index.row())
        header = self.__headerTexts[index.column()]
        try:
            if header == 'Name':
                item.setName(value)
            if header == 'Value':
                item.setValue(value)
            if header == 'Description':
                item.setDescription(value)
        except Exception as e:
            return False
        else:
            self.update()
            return True

