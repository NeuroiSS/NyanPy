from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys
import os
import re

from SyntaxHighlighterModule import *

class LineNumberArea(QtWidgets.QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.__editor = editor

    @override
    def sizeHint(self):
        return QtCore.QSize(self.__editor.lineNumberAreaWidth(), 0)

    @override
    def paintEvent(self, event):
        self.__editor.lineNumberAreaPaintEvent(event)


class CodeEditor(QtWidgets.QPlainTextEdit):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.__lineNumberArea = LineNumberArea(self)
        self.__filePath = ''
        self.__tabStyle = 'Hard tab' # or 'Soft tab'
        self.__syntaxHighlighter = SyntaxHighlighter(self.document())

        self.setupActions()
        self.setFont(QtGui.QFont('Courier', 9))
        self.updateWindowTitle()
        self.modificationChanged.connect(self.updateWindowTitle)

        # Tabstop/WrapMode/Whitespaces
        opt = QtGui.QTextOption()
        opt.setTabStopDistance(self.fontMetrics().horizontalAdvance('_') * 4)
        opt.setWrapMode(QtGui.QTextOption.NoWrap)
        opt.setFlags(QtGui.QTextOption.ShowTabsAndSpaces)
        self.document().setDefaultTextOption(opt)

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()

        self.setStyleSheet('QPlainTextEdit { font-family: Courier;'
            +'font-size: 9pt; background-color: #151515; color: #e8e8d3; }')

    def lineNumberAreaWidth(self):
        digits = 1
        maxNum = max(10, self.blockCount())
        while maxNum >= 10:
            maxNum //= 10
            digits += 1

        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    @override
    def resizeEvent(self, event):
        super().resizeEvent(event)

        # Resize line number area
        cr = self.contentsRect()
        rect = QtCore.QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height())
        self.__lineNumberArea.setGeometry(rect)

    @Slot()
    def lineNumberAreaPaintEvent(self, event):
        painter = QtGui.QPainter(self.__lineNumberArea)
        painter.fillRect(event.rect(), QtGui.QColor('#151515'))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        offset = self.contentOffset()
        top = self.blockBoundingGeometry(block).translated(offset).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                # Draw line number texts
                painter.setPen(QtGui.QColor('#605958'))
                painter.drawText(0, top, self.__lineNumberArea.width(), self.fontMetrics().height(), Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

        # QPainter needs and explicit end() in PyPy. This will become a context manager in 6.3.
        painter.end()

    @Slot()
    def updateLineNumberAreaWidth(self, newBlockCount):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    @Slot()
    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.__lineNumberArea.scroll(0, dy)
        else:
            width = self.__lineNumberArea.width()
            self.__lineNumberArea.update(0, rect.y(), width, rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    @Slot()
    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QtWidgets.QTextEdit.ExtraSelection()
            selection.format.setBackground(QtGui.QColor('#404040'))
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)

    @override
    def keyPressEvent(self, event):
        modifiers = event.modifiers()
        key = event.key()
        cursor = self.textCursor()
        blockText = cursor.block().text()
        
        if key == Qt.Key_Return:
            m = re.match(r'^\s*', blockText)
            spaces = m.group()
            self.insertPlainText('\n' + spaces)

        elif key == Qt.Key_Tab:
            if self.__tabStyle == 'Hard tab':
                # Hard tab
                self.insertPlainText('\t')
            else:
                # Soft tab
                leftText = blockText[:cursor.positionInBlock()]
                leftCount = len(leftText.replace('\t', '_' * 4))
                spaces = ' ' * (4 - leftCount % 4)
                self.insertPlainText(spaces)

        elif key == Qt.Key_Backspace:
            leftText = blockText[:cursor.positionInBlock()]
            leftCount = len(leftText.replace('\t', '_' * 4))
            check  = not cursor.hasSelection()
            check &= leftText.isspace()
            check &= leftText.endswith(' ')
            if check:
                count = (leftCount + 3) % 4 + 1
                for i in range(count):
                    cursor.deletePreviousChar()
            else:
                cursor.deletePreviousChar()
        else:
            super().keyPressEvent(event)

    def setupActions(self):
        action = QtGui.QAction('Open...', self)
        action.setShortcut('Ctrl+O')
        action.triggered.connect(self.openEvent)
        self.addAction(action)

        action = QtGui.QAction('Save', self)
        action.setShortcut('Ctrl+S')
        action.triggered.connect(self.saveEvent)
        self.addAction(action)

        action = QtGui.QAction('Save as...', self)
        action.setShortcut('Ctrl+Shift+S')
        action.triggered.connect(self.saveasEvent)
        self.addAction(action)

        action = QtGui.QAction('Hard tab', self)
        action.setCheckable(True)
        action.setChecked(self.__tabStyle == 'Hard tab')
        action.triggered.connect(self.setHardTab)
        self.addAction(action)

        action = QtGui.QAction('Soft tab', self)
        action.setCheckable(True)
        action.setChecked(self.__tabStyle == 'Soft tab')
        action.triggered.connect(self.setSoftTab)
        self.addAction(action)

        action = QtGui.QAction('Text', self)
        action.setCheckable(True)
        action.setChecked(True)
        action.triggered.connect(self.setSyntaxHighlighter)
        self.addAction(action)

        action = QtGui.QAction('Python', self)
        action.setCheckable(True)
        action.setChecked(False)
        action.triggered.connect(self.setSyntaxHighlighter_Python)
        self.addAction(action)

        action = QtGui.QAction('Matlab/GNU Octave', self)
        action.setCheckable(True)
        action.setChecked(False)
        action.triggered.connect(self.setSyntaxHighlighter_Matlab_GNUOctave)
        self.addAction(action)

    def action(self, text:str) -> QtGui.QAction:
        actions = {a.text():a for a in self.actions()}
        return actions[text]

    @Slot()
    def setSoftTab(self):
        self.__tabStyle = 'Soft tab'
        self.action('Soft tab').setChecked(True)
        self.action('Hard tab').setChecked(False)

    @Slot()
    def setHardTab(self):
        self.__tabStyle = 'Hard tab'
        self.action('Soft tab').setChecked(False)
        self.action('Hard tab').setChecked(True)

    @Slot()
    def setSyntaxHighlighter(self):
        self.__syntaxHighlighter.setDocument(None)
        self.__syntaxHighlighter = SyntaxHighlighter(self.document())
        self.action('Text').setChecked(True)
        self.action('Python').setChecked(False)
        self.action('Matlab/GNU Octave').setChecked(False)

    @Slot()
    def setSyntaxHighlighter_Python(self):
        self.__syntaxHighlighter.setDocument(None)
        self.__syntaxHighlighter = SyntaxHighlighter_Python(self.document())
        self.action('Text').setChecked(False)
        self.action('Python').setChecked(True)
        self.action('Matlab/GNU Octave').setChecked(False)

    @Slot()
    def setSyntaxHighlighter_Matlab_GNUOctave(self):
        self.__syntaxHighlighter.setDocument(None)
        self.__syntaxHighlighter = SyntaxHighlighter_Matlab_GNUOctave(self.document())
        self.action('Text').setChecked(False)
        self.action('Python').setChecked(False)
        self.action('Matlab/GNU Octave').setChecked(True)

    @Slot()
    def updateWindowTitle(self):
        title = os.path.basename(self.__filePath) if self.__filePath else 'New'
        if self.document().isModified():
            title = '*' + title
        self.setWindowTitle(title)
        self.windowTitleChanged.emit(title)

    def setFilePath(self, filePath):
        self.__filePath = filePath
        self.updateWindowTitle()

    @Slot()
    def openEvent(self):
        if self.document().isModified():
            msgBox = QtWidgets.QMessageBox(self)
            msgBox.setText('Discard changes?')
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            ans = msgBox.exec()
            if ans == QtWidgets.QMessageBox.Cancel:
                return

        filePath, selectedFilter = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', '', 'All Files (*)')
        if not filePath:
            return

        try:
            with open(filePath, 'r') as f:
                self.setPlainText(f.read())
                self.setFilePath(filePath)
                self.document().setModified(False)

                root, ext = os.path.splitext(filePath)
                ext = ext.lower()
                if ext in ['.py', '.pyw']:
                    self.setSyntaxHighlighter_Python()
                    self.setSoftTab() # Soft tabs are preferred in Python.
                elif ext in ['.m']:
                    self.setSyntaxHighlighter_Matlab_GNUOctave()
                else:
                    self.setSyntaxHighlighter()

        except Exception as e:
            msgBox = QtWidgets.QMessageBox(self)
            msgBox.setText(str(e))
            msgBox.exec()

    @Slot()
    def saveEvent(self):
        if not self.__filePath:
            self.saveasEvent()
            return

        try:
            with open(self.__filePath, 'w', encoding = 'utf-8') as f:
                f.write(self.toPlainText())
                self.document().setModified(False)

        except Exception as e:
            msgBox = QtWidgets.QMessageBox(self)
            msgBox.setText(str(e))
            msgBox.exec()

    @Slot()
    def saveasEvent(self):
        dir_ = ''
        if self.__filePath and os.path.isdir(os.path.dirname(self.__filePath)):
            dir_ = os.path.dirname(self.__filePath)

        filePath, selectedFilter = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', dir_, 'All Files (*)')
        if not filePath:
            return

        try:
            with open(filePath, 'w', encoding = 'utf-8') as f:
                f.write(self.toPlainText())
                self.document().setModified(False)
                self.setFilePath(filePath)

        except Exception as e:
            msgBox = QtWidgets.QMessageBox(self)
            msgBox.setText(str(e))
            msgBox.exec()

