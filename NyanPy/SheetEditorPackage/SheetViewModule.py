from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
from enum import Enum
from numpy import *
import numpy
import re
import sys
import os

from SheetModelModule import SheetModel
from SheetCmdsModule import *
from SheetFindReplaceModule import SheetFindReplace
from VariablesPackage.VariableItemListModule import VariableItemList
from PlottingPackage.DataListItemModule import DataListItem

class Modes(Enum):
    NORMAL = 0
    INSERT = 2
    INSERT_LINE = 3
    VISUAL = 4
    VISUAL_LINE = 5

class SheetView(QtWidgets.QTableView):

    # Signals
    modeChanged = Signal(Modes)
    commandRequested = Signal()
    filePathChanged = Signal(str)
    plottingRequested = Signal(list)

    def __init__(self, parent = None):
        super().__init__(parent)
        # Model
        self.__model = SheetModel()
        self.setModel(self.__model)
        # Undo stack
        self.__undoStack = self.__model.undoStack()
        self.__undoStack.indexChanged.connect(self.updateWindowTitle)
        # Selection model
        self.__selection = self.selectionModel()
        # Editor mode
        self.__MODE = Modes.NORMAL
        # File path
        self.__filePath = ''
        # Start index for VISUAL mode
        self.__topLeft = QtCore.QModelIndex()
        self.__lastKey = 0
        # Add actions
        menu = self.createMenuActions()
        self.addActions(menu.actions())
        # Variables
        self.__list = VariableItemList()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenuEvent)
        self.verticalHeader().setDefaultSectionSize(20)
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setObjectName('SheetView')
        self.updateWindowTitle()
        # Set cursor to (0, 0)
        self.setCurrentIndex(self.__model.index(0, 0))

    def mode(self):
        return self.__MODE

    def path(self):
        return self.__filePath

    def list(self):
        return self.__list

    def changeMode(self, mode:Modes):
        curr = self.currentIndex()
        if mode in [Modes.VISUAL, Modes.VISUAL_LINE]:
            self.__selection.clear()
            self.setCurrentIndex(curr)
            self.__topLeft = curr
            self.__lastKey = 0

        self.__MODE = mode
        self.updateActions(self.actions())
        self.modeChanged.emit(mode)

        # Initially select column for VISUAL-LINE mode
        if mode == Modes.VISUAL_LINE:
            self.cursorMoveEvent(Qt.Key_L, Qt.NoModifier)

    def setPath(self, path:str):
        self.__filePath = path
        self.updateWindowTitle()
        self.filePathChanged.emit(path)

    @override
    def keyPressEvent(self, e:QtGui.QKeyEvent):
        key = e.key()
        mod = e.modifiers()
        remap = { Qt.Key_Left : Qt.Key_H,\
                  Qt.Key_Down : Qt.Key_J,\
                  Qt.Key_Up   : Qt.Key_K,\
                  Qt.Key_Right: Qt.Key_L }
        if key in remap:
            key = remap[key]

        curr = self.currentIndex()
        if key == Qt.Key_Return and not self.isPersistentEditorOpen(curr):
            self.edit(curr)
            return

        elif key == Qt.Key_Colon:
            self.commandRequested.emit()
            return

        elif key in [Qt.Key_H, Qt.Key_J, Qt.Key_K, Qt.Key_L]:
            if self.__MODE != Modes.VISUAL_LINE or key == self.__lastKey:
                if key == Qt.Key_J and curr.row() == self.__model.rowCount() - 1:
                    self.extendRow()
                if key == Qt.Key_L and curr.column() == self.__model.columnCount() - 1:
                    self.extendColumn()
            self.cursorMoveEvent(key, mod)
            return

        e = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, key, mod, e.text())
        super().keyPressEvent(e)

    def cursorMoveEvent(self, key, mod) -> bool:
        if key not in [Qt.Key_H, Qt.Key_J, Qt.Key_K, Qt.Key_L]:
            return False

        SelectionFlags = QtCore.QItemSelectionModel.SelectionFlags
        orient = lambda key: \
                Qt.Horizontal if key in [Qt.Key_H, Qt.Key_L]\
                else Qt.Vertical if key in [Qt.Key_J, Qt.Key_K]\
                else None

        scroll = lambda index: self.scrollTo(index, QtWidgets.QAbstractItemView.PositionAtCenter)

        if self.__MODE == Modes.NORMAL:
            index = self.cursorIndex(key, mod)
            self.__selection.clear()
            self.setCurrentIndex(index)
            scroll(index)
            return True

        elif self.__MODE == Modes.VISUAL:
            index = self.cursorIndex(key, mod)
            flags = SelectionFlags.Clear | SelectionFlags.SelectCurrent

            selection = QtCore.QItemSelection()
            selection.select(self.__topLeft, index)
            self.__selection.select(selection, flags)
            self.__selection.setCurrentIndex(index, SelectionFlags.NoUpdate)
            scroll(index)
            return True

        elif self.__MODE == Modes.VISUAL_LINE:
            index = self.cursorIndex(key, mod) if orient(key) == orient(self.__lastKey)\
                    else self.currentIndex()

            flags = SelectionFlags.Columns if orient(key) == Qt.Horizontal\
                    else SelectionFlags.Rows
            flags |= SelectionFlags.Clear
            flags |= SelectionFlags.SelectCurrent

            selection = QtCore.QItemSelection()
            selection.select(self.__topLeft, index)
            self.__selection.select(selection, flags | SelectionFlags.SelectCurrent)
            self.__selection.setCurrentIndex(index, SelectionFlags.NoUpdate)
            scroll(index)
            self.__lastKey = key
            return True

        return False

    def cursorIndex(self, key:int, mod:Qt.KeyboardModifiers) -> QtCore.QModelIndex:
        curr = self.currentIndex()
        CTRL = mod & (Qt.ControlModifier | Qt.ShiftModifier)
        dirKeys = { Qt.Key_H: (0, -1),\
                    Qt.Key_J: (+1, 0),\
                    Qt.Key_K: (-1, 0),\
                    Qt.Key_L: (0, +1) }
        if key not in dirKeys:
            return curr

        rowIncr, colIncr = dirKeys[key]
        if not CTRL:
            row = curr.row() + rowIncr
            col = curr.column() + colIncr
            index = self.__model.index(row, col)
            return index if index.isValid() else curr

        currType = type(self.__model.data(curr))
        index = curr
        cnt = 0
        while True:
            row = index.row() + rowIncr
            col = index.column() + colIncr
            next = self.__model.index(row, col)
            if not next.isValid():
                break
            if type(self.__model.data(next)) is not currType:
                if cnt == 0:
                    index = next
                break
            cnt += 1
            index = next

        return index

    @Slot()
    def updateWindowTitle(self):
        title = os.path.basename(self.__filePath) if self.__filePath else 'New'
        try:
            if not self.__undoStack.isClean():
                title = '*' + title
            self.setWindowTitle(title)
            self.windowTitleChanged.emit(title)
        except Exception:
            pass

    def createMenuActions(self) -> QtWidgets.QMenu:
        menu = QtWidgets.QMenu(self)
        action = menu.addAction('Copy (yank)')
        action.setShortcuts(['Ctrl+C', 'Y'])
        action.triggered.connect(self.copy)
        action = menu.addAction('Paste (put)')
        action.setShortcuts(['Ctrl+V', 'P'])
        action.triggered.connect(self.paste)
        action = menu.addAction('Delete')
        action.setShortcut('Del')
        action.triggered.connect(self.delete)
        action = menu.addAction('Cut (delete)')
        action.setShortcuts(['Ctrl+X', 'D'])
        action.triggered.connect(self.cut)
        action = menu.addAction('Find && Replace')
        action.setShortcut('Ctrl+F')
        action.triggered.connect(self.findReplace)
        action = self.__undoStack.createUndoAction(self)
        action.setShortcuts(['Ctrl+Z', 'U'])
        menu.addAction(action)
        action = self.__undoStack.createRedoAction(self)
        action.setShortcuts(['Ctrl+Y', 'Ctrl+R'])
        menu.addAction(action)
        menu.addSeparator()
        action = menu.addAction('New')
        action.setShortcut('Ctrl+N')
        action.triggered.connect(self.new)
        action = menu.addAction('Open...')
        action.setShortcut('Ctrl+O')
        action.triggered.connect(self.open)
        action = menu.addAction('Save')
        action.setShortcut('Ctrl+S')
        action.triggered.connect(self.save)
        action = menu.addAction('Save as...')
        action.setShortcut('Ctrl+Shift+S')
        action.triggered.connect(self.saveas)
        menu.addSeparator()
        action = menu.addAction('NORMAL mode')
        action.setShortcuts(['Esc', 'Ctrl+['])
        action.triggered.connect(lambda: self.changeMode(Modes.NORMAL))
        action = menu.addAction('INSERT mode')
        action.setShortcut('I')
        action.triggered.connect(lambda: self.changeMode(Modes.INSERT))
        action = menu.addAction('INSERT-LINE mode')
        action.setShortcut('Shift+I')
        action.triggered.connect(lambda: self.changeMode(Modes.INSERT_LINE))
        action = menu.addAction('VISUAL mode')
        action.setShortcut('V')
        action.triggered.connect(lambda: self.changeMode(Modes.VISUAL))
        action = menu.addAction('VISUAL-LINE mode')
        action.setShortcut('Shift+V')
        action.triggered.connect(lambda: self.changeMode(Modes.VISUAL_LINE))
        menu.addSeparator()
        action = menu.addAction('Insert Row')
        action.setShortcut('J')
        action.triggered.connect(self.insertRow)
        action = menu.addAction('Insert Column')
        action.setShortcut('L')
        action.triggered.connect(self.insertColumn)
        action = menu.addAction('Remove Row')
        action.setShortcut('K')
        action.triggered.connect(self.removeRow)
        action = menu.addAction('Remove Column')
        action.setShortcut('H')
        action.triggered.connect(self.removeColumn)
        menu.addSeparator()
        action = menu.addAction('Scientific Format')
        action.setShortcut('E')
        action.triggered.connect(lambda: self.__model.setNumStr('{:e}'))
        action = menu.addAction('Fixed-Point Format')
        action.setShortcut('F')
        action.triggered.connect(lambda: self.__model.setNumStr('{:f}'))
        action = menu.addAction('General Format')
        action.setShortcut('G')
        action.triggered.connect(lambda: self.__model.setNumStr('{:g}'))
        menu.addSeparator()
        action = menu.addAction('Set Variable')
        action.setShortcut('S')
        action.triggered.connect(self.setVariable)
        action = menu.addAction('Put Variable')
        action.setShortcut('Shift+P')
        action.triggered.connect(self.putVariable)
        action = menu.addAction('Add to Plotting List')
        action.setShortcut('A')
        action.triggered.connect(self.addPlot)

        self.updateActions(menu.actions())
        return menu

    def updateActions(self, actions:list):
        # list --> dict
        actions = {a.text(): a for a in actions}
        actions['NORMAL mode'].setEnabled(self.__MODE != Modes.NORMAL)
        actions['INSERT mode'].setEnabled(self.__MODE != Modes.INSERT)
        actions['INSERT-LINE mode'].setEnabled(self.__MODE != Modes.INSERT_LINE)
        actions['VISUAL mode'].setEnabled(self.__MODE != Modes.VISUAL)
        actions['VISUAL-LINE mode'].setEnabled(self.__MODE != Modes.VISUAL_LINE)
        actions['Insert Row'].setEnabled(self.__MODE in [Modes.INSERT, Modes.INSERT_LINE])
        actions['Insert Column'].setEnabled(self.__MODE in [Modes.INSERT, Modes.INSERT_LINE])
        actions['Remove Row'].setEnabled(self.__MODE in [Modes.INSERT, Modes.INSERT_LINE])
        actions['Remove Column'].setEnabled(self.__MODE in [Modes.INSERT, Modes.INSERT_LINE])

    @override
    def focusInEvent(self, event):
        # Activate actions
        for action in self.actions():
            action.setEnabled(True)

        self.updateActions(self.actions())

    @override
    def focusOutEvent(self, event):
        # Inactivate actions
        for action in self.actions():
            action.setEnabled(False)

    @Slot()
    def contextMenuEvent(self, pos:QtCore.QPoint):
        contextMenu = self.createMenuActions()
        contextMenu.exec(self.mapToGlobal(pos))

    @Slot()
    def copy(self):
        selected = self.selectedIndexes()
        if not selected:
            return
        numTypes = [float, complex, float32, float64, complex64, complex128]
        delimiter = ','
        lines = []
        rows = [index.row() for index in selected]
        rows = sorted(set(rows))
        for row in rows:
            cols = [index.column() for index in selected]
            cols = sorted(set(cols))
            line = []
            for col in cols:
                index = self.__model.index(row, col)
                value = self.__model.data(index)
                if not value:
                    continue
                if type(value) in numTypes:
                    line.append('{:.14e}'.format(value))
                elif type(value) is str and delimiter in value:
                    line.append('"'+value+'"')
                elif type(value) is str:
                    line.append(value)
                else:
                    line.append(str(value))
            if line:
                lines.append(line)
        text = ''
        for line in lines:
            text += delimiter.join(line) + '\n'
        clipboard = QtGui.QGuiApplication.clipboard()
        clipboard.setText(text)

        # Return to NORMAL mode
        self.changeMode(Modes.NORMAL)

    @Slot()
    def paste(self):
        curr = self.currentIndex()
        mimeData = QtGui.QGuiApplication.clipboard().mimeData()
        if not mimeData.hasText():
            return
        delimiter = ','
        lines = []
        for text in mimeData.text().splitlines():
            line = self.__model.split(text)
            lines.append(line)
        rowCount = len(lines)
        cols = [len(line) for line in lines]
        colCount = max(cols) if cols else 0

        self.__undoStack.beginMacro('Paste')
        if curr.row() + rowCount > self.__model.rowCount():
            pos = self.__model.rowCount()
            cnt = curr.row() + rowCount - pos
            self.__undoStack.push(InsertRowsCmd(self.__model, pos, cnt))
        if curr.column() + colCount > self.__model.columnCount():
            pos = self.__model.columnCount()
            cnt = curr.column() + colCount - pos
            self.__undoStack.push(InsertColumnsCmd(self.__model, pos, cnt))

        indices = []
        values = []
        for row, line in enumerate(lines):
            for col, value in enumerate(line):
                indices += [self.__model.index(curr.row() + row, curr.column() + col)]
                values += [value]
        self.__undoStack.push(SetCmd(self.__model, indices, values))
        self.__undoStack.endMacro()

        # Return to NORMAL mode
        self.changeMode(Modes.NORMAL)

    @Slot()
    def delete(self):
        selected = self.selectedIndexes()
        if not selected:
            return
        self.__undoStack.push(DeleteCmd(self.__model, selected))

        # Return to NORMAL mode
        self.changeMode(Modes.NORMAL)

    @Slot()
    def cut(self):
        self.copy()
        self.delete()

        # Return to NORMAL mode
        self.changeMode(Modes.NORMAL)

    @Slot()
    def findReplace(self):
        dialog = SheetFindReplace(self)
        ans = dialog.exec()
        if ans != QtWidgets.QDialog.Accepted:
            return

        # Search scope
        scope = dialog.scope()
        indices = self.__model.indices() if scope == 'All'\
                else self.selectedIndexes()

        # Find
        for index in indices:
            value = self.__model.data(index)
            if type(value) is not str:
                continue
            if re.search(dialog.find(), value):
                self.__selection.select(index, QtCore.QItemSelectionModel.Select)

        # Replace
        checked, text = dialog.replace()
        if checked:
            selected = self.selectedIndexes()
            if not selected:
                return
            values = [text for index in selected]
            self.__undoStack.push(SetCmd(self.__model, selected, values, 'Replace'))

    @Slot()
    def new(self):
        if not self.__undoStack.isClean():
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText('Discard changes?')
            msgbox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            if msgbox.exec() == QtWidgets.QMessageBox.Cancel:
                return

        self.__model.clear()
        self.__undoStack.clear()
        self.setPath('')

        # Return to NORMAL mode
        self.changeMode(Modes.NORMAL)

    @Slot()
    def open(self, path = ''):
        if not self.__undoStack.isClean():
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText('Discard changes?')
            msgbox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            if msgbox.exec() == QtWidgets.QMessageBox.Cancel:
                return

        if not path:
            path, selectedFilter = QtWidgets.QFileDialog.getOpenFileName(self,\
                    'Open File', '', 'CSV Files (*.csv);;All Files (*)')
        if not path:
            return

        base, ext = os.path.splitext(path)
        fileType = 'CSV' if ext.lower() == '.csv' else 'TXT'
        try:
            self.__model.load(path, fileType)
            self.__undoStack.clear()
            self.__undoStack.setClean()
            self.setPath(path)

        except Exception as e:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText(str(e))
            msgbox.exec()

        # Return to NORMAL mode
        self.changeMode(Modes.NORMAL)

    @Slot()
    def save(self):
        base, ext = os.path.splitext(self.__filePath)
        if ext.lower() != '.csv':
            self.saveas()
            return
        try:
            self.__model.write(self.__filePath)
            self.__undoStack.setClean()
            self.updateWindowTitle()

        except Exception as e:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText(str(e))
            msgbox.exec()

        # Return to NORMAL mode
        self.changeMode(Modes.NORMAL)

    @Slot()
    def saveas(self):
        directory = os.path.dirname(self.__filePath)
        path, selectedFilter = QtWidgets.QFileDialog.getSaveFileName(self,\
                'Save File', directory, 'CSV Files (*.csv)')
        if not path:
            return
        try:
            self.__model.write(path)
            self.__undoStack.setClean()
            self.setPath(path)

        except Exception as e:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText(str(e))
            msgbox.exec()

        # Return to NORMAL mode
        self.changeMode(Modes.NORMAL)

    @Slot()
    def extendRow(self):
        rowCount = self.__model.rowCount()
        self.__undoStack.push(InsertRowsCmd(self.__model, rowCount, 1))

    @Slot()
    def extendColumn(self):
        colCount = self.__model.columnCount()
        self.__undoStack.push(InsertColumnsCmd(self.__model, colCount, 1))

    @Slot()
    def insertRow(self):
        if self.__MODE == Modes.INSERT:
            self.insertRow_selected()
        elif self.__MODE == Modes.INSERT_LINE:
            self.insertRow_line()

    @Slot()
    def insertColumn(self):
        if self.__MODE == Modes.INSERT:
            self.insertColumn_selected()
        elif self.__MODE == Modes.INSERT_LINE:
            self.insertColumn_line()

    @Slot()
    def removeRow(self):
        if self.__MODE == Modes.INSERT:
            self.removeRow_selected()
        elif self.__MODE == Modes.INSERT_LINE:
            self.removeRow_line()

    @Slot()
    def removeColumn(self):
        if self.__MODE == Modes.INSERT:
            self.removeColumn_selected()
        elif self.__MODE == Modes.INSERT_LINE:
            self.removeColumn_line()

    def insertRow_line(self):
        curr = self.currentIndex()
        self.__undoStack.push(InsertRowsCmd(self.__model, curr.row(), 1))

        # Clear selection and keep cursor position
        self.__selection.clear()
        self.setCurrentIndex(curr)

    def insertColumn_line(self):
        curr = self.currentIndex()
        self.__undoStack.push(InsertColumnsCmd(self.__model, curr.column(), 1))

        # Clear selection and keep cursor position
        self.__selection.clear()
        self.setCurrentIndex(curr)

    def insertRow_selected(self):
        selected = self.selectedIndexes()
        curr = self.currentIndex()
        if not selected:
            return

        selectedCols = [index.column() for index in selected]
        selectedCols = set(selectedCols)
        rowCount = self.__model.rowCount()

        values = []
        srcIndices = []
        dstIndices = []

        for index in self.__model.indices():
            row = index.row()
            col = index.column()
            if col not in selectedCols:
                continue
            if row >= curr.row():
                values += [self.__model.data(index)]
                srcIndices += [index]
                dstIndices += [self.__model.index(row + 1, col)]

        self.__undoStack.beginMacro('Insert Rows')
        self.__undoStack.push(InsertRowsCmd(self.__model, rowCount, 1))
        self.__undoStack.push(DeleteCmd(self.__model, srcIndices))
        self.__undoStack.push(SetCmd(self.__model, dstIndices, values))
        self.__undoStack.endMacro()

    def insertColumn_selected(self):
        selected = self.selectedIndexes()
        curr = self.currentIndex()
        if not selected:
            return

        selectedRows = [index.row() for index in selected]
        selectedRows = set(selectedRows)
        colCount = self.__model.columnCount()

        values = []
        srcIndices = []
        dstIndices = []

        for index in self.__model.indices():
            row = index.row()
            col = index.column()
            if row not in selectedRows:
                continue
            if col >= curr.column():
                values += [self.__model.data(index)]
                srcIndices += [index]
                dstIndices += [self.__model.index(row, col + 1)]

        self.__undoStack.beginMacro('Insert Columns')
        self.__undoStack.push(InsertColumnsCmd(self.__model, colCount, 1))
        self.__undoStack.push(DeleteCmd(self.__model, srcIndices))
        self.__undoStack.push(SetCmd(self.__model, dstIndices, values))
        self.__undoStack.endMacro()

    def removeRow_line(self):
        if self.__model.rowCount() == 1:
            return

        curr = self.currentIndex()
        indices = [index for index in self.__model.indices() if index.row() == curr.row()]

        self.__undoStack.beginMacro('Remove Rows')
        self.__undoStack.push(DeleteCmd(self.__model, indices))
        self.__undoStack.push(RemoveRowsCmd(self.__model, curr.row(), 1))
        self.__undoStack.endMacro()

        # Clear selection and move cursor
        cursorIndex = self.__model.index(curr.row(), curr.column())
        if not cursorIndex.isValid():
            cursorIndex = self.__model.index(curr.row() - 1, curr.column())

        self.__selection.clear()
        self.setCurrentIndex(cursorIndex)

    def removeColumn_line(self):
        if self.__model.columnCount() == 1:
            return

        curr = self.currentIndex()
        indices = [index for index in self.__model.indices() if index.column() == curr.column()]

        self.__undoStack.beginMacro('Remove Columns')
        self.__undoStack.push(DeleteCmd(self.__model, indices))
        self.__undoStack.push(RemoveColumnsCmd(self.__model, curr.column(), 1))
        self.__undoStack.endMacro()

        # Clear selection and move cursor
        cursorIndex = self.__model.index(curr.row(), curr.column())
        if not cursorIndex.isValid():
            cursorIndex = self.__model.index(curr.row(), curr.column() - 1)

        self.__selection.clear()
        self.setCurrentIndex(cursorIndex)

    def removeRow_selected(self):
        selected = self.selectedIndexes()
        curr = self.currentIndex()
        if not selected:
            return

        selectedCols = [index.column() for index in selected]
        selectedCols = set(selectedCols)

        values = []
        delIndices = []
        srcIndices = []
        dstIndices = []

        for index in self.__model.indices():
            row = index.row()
            col = index.column()
            if col not in selectedCols:
                continue
            if row == curr.row():
                delIndices += [index]
            elif row > curr.row():
                values += [self.__model.data(index)]
                srcIndices += [index]
                dstIndices += [self.__model.index(row - 1, col)]

        self.__undoStack.beginMacro('Remove Rows')
        self.__undoStack.push(DeleteCmd(self.__model, delIndices))
        self.__undoStack.push(DeleteCmd(self.__model, srcIndices))
        self.__undoStack.push(SetCmd(self.__model, dstIndices, values))
        self.__undoStack.endMacro()

    def removeColumn_selected(self):
        selected = self.selectedIndexes()
        curr = self.currentIndex()
        if not selected:
            return

        selectedRows = [index.row() for index in selected]
        selectedRows = set(selectedRows)

        values = []
        delIndices = []
        srcIndices = []
        dstIndices = []

        for index in self.__model.indices():
            row = index.row()
            col = index.column()
            if row not in selectedRows:
                continue
            if col == curr.column():
                delIndices += [index]
            elif col > curr.column():
                values += [self.__model.data(index)]
                srcIndices += [index]
                dstIndices += [self.__model.index(row, col - 1)]

        self.__undoStack.beginMacro('Remove Columns')
        self.__undoStack.push(DeleteCmd(self.__model, delIndices))
        self.__undoStack.push(DeleteCmd(self.__model, srcIndices))
        self.__undoStack.push(SetCmd(self.__model, dstIndices, values))
        self.__undoStack.endMacro()

    @Slot()
    def setVariable(self):
        selected = self.selectedIndexes()
        if not selected:
            return
        numTypes = [int, float, complex, int32, int64, float32, float64, complex64, complex128]

        data = [self.__model.data(index) for index in selected]
        nums = [x for x in data if type(x) in numTypes]
        strs = [x for x in data if type(x) is str]
        if not nums:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText('No numbers selected')
            msgbox.exec()
            return

        # Guess name
        names = []
        if strs:
            guessName = strs[0]
            guessName = re.sub(r'[^a-zA-Z_0-9]+', '', guessName)
            guessName = re.sub(r'^(?=[0-9])', '_', guessName)
            names.append(guessName)

        names += self.__list.names()
        name, ok = QtWidgets.QInputDialog.getItem(self, 'Set Variable', 'Name:', names, 0, True)
        if not ok:
            return

        if not re.match(r'[a-zA-Z_][a-zA-Z_0-9]*$', name):
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText('Invalid name')
            msgbox.exec()
            return

        if len(nums) == 1:
            value = nums[0]
            self.__list.append(name, value)
        else:
            value = array(nums)
            self.__list.append(name, value)

        # Return to NORMAL mode
        self.changeMode(Modes.NORMAL)

    @Slot()
    def putVariable(self):
        names = self.__list.names()
        expression, ok = QtWidgets.QInputDialog.getItem(self, 'Put Variable',\
                'Expression:', names, 0, True)
        if not ok or not expression:
            return

        # Evaluate expression
        globals = vars(numpy)
        locals = {}
        self.__list.eval(locals)
        try:
            eval_ = eval(expression, globals, locals)

        except Exception as e:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText(str(e))
            msgbox.exec()
            return

        curr = self.currentIndex()
        if type(eval_) in [list, ndarray]:
            # Insert Rows
            self.__undoStack.beginMacro('Put Variable')
            rowCount = self.__model.rowCount()
            if curr.row() + len(eval_) > rowCount:
                self.__undoStack.push(InsertRowsCmd(self.__model,\
                        rowCount, curr.row() + len(eval_) - rowCount))
            # Set
            indices = [self.__model.index(curr.row() + cnt, curr.column())\
                    for cnt in range(len(eval_))]
            self.__undoStack.push(SetCmd(self.__model, indices, list(eval_)))
            self.__undoStack.endMacro()
        else:
            # Set
            self.__undoStack.push(SetCmd(self.__model, [curr], [eval_], 'Put Variable'))

        # Return to NORMAL mode
        self.changeMode(Modes.NORMAL)

    @Slot()
    def addPlot(self):
        selected = self.selectedIndexes()
        if not selected:
            return

        cols = [index.column() for index in selected]
        cols = set(cols)
        y = {}
        for col in cols:
            data = [self.__model.data(index) for index in selected if index.column() == col]
            nums = [x for x in data if type(x) != str]
            strs = [x for x in data if type(x) == str]
            if not nums:
                continue
            for i, num in enumerate(nums):
                try:
                    nums[i] = float(num)
                except Exception:
                    nums[i] = float('nan')
            name = strs[0] if strs else 'column {:d}'.format(col)
            y[name] = nums

        if not y:
            return

        # Check data lengths
        lengths = [len(nums) for nums in y.values()]
        if len(set(lengths)) > 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText('Selected vectors have different lengths.')
            msgbox.exec()
            return
        
        # Get X vector
        names = ['none']
        names += list(y.keys())
        name, ok = QtWidgets.QInputDialog.getItem(self, 'Add to Plotting List', 'X vector:', names, 0, False)
        if not ok:
            return
        if name != 'none':
            x = y.pop(name)
        else:
            x = list(range(lengths[0]))

        # DataListItems
        items = []
        for name in y:
            source, ext = os.path.splitext(os.path.basename(self.__filePath))
            dataname = name+', '+source if source else name

            item = DataListItem(dataname)
            item.setX(x)
            item.setY(y[name])
            item.setLegendText(dataname)
            items.append(item)

        # Emit plottingRequested() signal
        self.plottingRequested.emit(items)

        # Return to NORMAL mode
        self.changeMode(Modes.NORMAL)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = SheetView()
    ex.show()
    sys.exit(app.exec())

