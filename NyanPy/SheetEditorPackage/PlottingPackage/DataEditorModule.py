from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override

class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, item, parent = None):
        super().__init__(parent)
        self.__x = item.x().copy()
        self.__y = item.y().copy()

    def x(self):
        return self.__x

    def y(self):
        return self.__y

    @override
    def rowCount(self, parent:QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return len(self.__x) if not parent.isValid() else 0

    @override
    def columnCount(self, parent:QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return 2

    @override
    def headerData(self, section:int, orientation:Qt.Orientation, role:int = Qt.DisplayRole):
        # Horizontal header
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return 'x' if section == 0\
                    else 'y' if section == 1\
                    else None
        # Vertical header
        if role == Qt.DisplayRole and orientation == Qt.Vertical:
            return str(section + 1)

        return None

    @override
    def flags(self, index:QtCore.QModelIndex) -> Qt.ItemFlags:
        return Qt.ItemIsEditable | super().flags(index) if index.isValid()\
                else Qt.NoItemFlags

    @override
    def data(self, index:QtCore.QModelIndex, role:int = Qt.DisplayRole):
        if not index.isValid() or role not in [Qt.DisplayRole, Qt.EditRole]:
            return None
        return '{:g}'.format(self.__x[index.row()]) if index.column() == 0\
                else '{:g}'.format(self.__y[index.row()]) if index.column() == 1\
                else None
        
    @override
    def setData(self, index:QtCore.QModelIndex, value, role:int = Qt.EditRole) -> bool:
        if role != Qt.EditRole or not index.isValid():
            return False
        try:
            num = float(value)
        except Exception:
            num = float('nan')
        # X
        if index.column() == 0:
            self.__x[index.row()] = num
            return True
        # Y
        elif index.column() == 1:
            self.__y[index.row()] = num
            return True
        else:
            return False

class DataEditor(QtWidgets.QDialog):

    def __init__(self, item, parent = None):
        super().__init__(parent)
        self.__item = item
        self.__model = TableModel(item)

        table = QtWidgets.QTableView()
        table.setModel(self.__model)
        table.verticalHeader().setDefaultSectionSize(20)
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok\
                | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        vboxlayout = QtWidgets.QVBoxLayout(self)
        vboxlayout.addWidget(table)
        vboxlayout.addWidget(buttonBox)
        self.setWindowTitle('Data Editor')

    @override
    def accept(self):
        self.__item.setX(self.__model.x())
        self.__item.setY(self.__model.y())
        super().accept()

