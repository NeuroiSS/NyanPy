from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override

class SetCmd(QtGui.QUndoCommand):

    def __init__(self, model, indices:list, new:list, text:str = 'Set', parent = None):
        super().__init__(text, parent)
        if len(indices) != len(new):
            raise IndexError("'indices' and 'new' have different lengths")
        self.__model = model
        self.__indices = indices
        self.__new = new
        self.__old = [model.data(index) for index in indices]

    @override
    def redo(self):
        for i, index in enumerate(self.__indices):
            self.__model.setData(index, self.__new[i])

    @override
    def undo(self):
        for i, index in enumerate(self.__indices):
            self.__model.setData(index, self.__old[i])


class DeleteCmd(SetCmd):

    def __init__(self, model, indices:list, text:str = 'Delete', parent = None):
        new = [None for index in indices]
        super().__init__(model, indices, new, text, parent)


class InsertRowsCmd(QtGui.QUndoCommand):

    def __init__(self, model, pos:int, cnt:int, text:str = 'Insert Rows', parent = None):
        super().__init__(text, parent)
        self.__model = model
        self.__pos = pos
        self.__cnt = cnt

    @override
    def redo(self):
        self.__model.insertRows(self.__pos, self.__cnt)

    @override
    def undo(self):
        self.__model.removeRows(self.__pos, self.__cnt)


class InsertColumnsCmd(QtGui.QUndoCommand):

    def __init__(self, model, pos:int, cnt:int, text:str = 'Insert Columns', parent = None):
        super().__init__(text, parent)
        self.__model = model
        self.__pos = pos
        self.__cnt = cnt

    @override
    def redo(self):
        self.__model.insertColumns(self.__pos, self.__cnt)

    @override
    def undo(self):
        self.__model.removeColumns(self.__pos, self.__cnt)


class RemoveRowsCmd(DeleteCmd):

    def __init__(self, model, pos:int, cnt:int, text:str = 'Remove Rows', parent = None):
        indices = [index for index in model.indices() if pos <= index.row() < pos + cnt]
        super().__init__(model, indices, text, parent)
        self.__model = model
        self.__pos = pos
        self.__cnt = cnt

    @override
    def redo(self):
        super().redo()
        self.__model.removeRows(self.__pos, self.__cnt)

    @override
    def undo(self):
        self.__model.insertRows(self.__pos, self.__cnt)
        super().undo()


class RemoveColumnsCmd(DeleteCmd):

    def __init__(self, model, pos:int, cnt:int, text:str = 'Remove Columns', parent = None):
        indices = [index for index in model.indices() if pos <= index.column() < pos + cnt]
        super().__init__(model, indices, text, parent)
        self.__model = model
        self.__pos = pos
        self.__cnt = cnt

    @override
    def redo(self):
        super().redo()
        self.__model.removeColumns(self.__pos, self.__cnt)

    @override
    def undo(self):
        self.__model.insertColumns(self.__pos, self.__cnt)
        super().undo()

