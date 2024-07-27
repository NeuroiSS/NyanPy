from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys
import os

from SheetViewModule import Modes

class CommandInput(QtWidgets.QWidget):

    # Signals
    commandEntered = Signal(str)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.__commandText = ''
        self.__headText = 'Command:'
        self.__cursorState = False
        self.__timer = QtCore.QTimer(self)
        self.__timer.timeout.connect(self.blinkCursor)

        self.setFocusPolicy(Qt.ClickFocus)

    @override
    def sizeHint(self):
        return QtCore.QSize(300, 12)

    @override
    def keyPressEvent(self, event):
        key = event.key()
        if key >= Qt.Key_A and key <= Qt.Key_Z:
            if len(self.__commandText) == 20:
                return
            self.__commandText += event.text()
            self.update()
        
        elif key == Qt.Key_Backspace:
            self.__commandText = self.__commandText[:-1]
            self.update()
        
        elif key == Qt.Key_Return:
            self.commandEntered.emit(self.__commandText)
            self.__commandText = ''
            self.update()

        elif key == Qt.Key_Escape:
            self.__commandText = ''
            self.commandEntered.emit('')
            self.update()
    
    @Slot()
    def blinkCursor(self):
        self.__cursorState = not self.__cursorState
        self.update()

    @override
    def focusInEvent(self, event):
        self.__cursorState = True
        self.__timer.start(500)
        self.update()

    @override
    def focusOutEvent(self, event):
        self.__timer.stop()
        self.__cursorState = False
        self.update()

    @override
    def paintEvent(self, event):
        rect = self.rect()
        painter = QtGui.QPainter(self)
        painter.fillRect(rect, QtGui.QColor('#151515'))
        painter.setPen(QtGui.QColor('#e8e8d3'))
        painter.setFont(QtGui.QFont('Courier', 9))
        fontMetrics = painter.fontMetrics()
        height = rect.height()
        ascent = fontMetrics.ascent()
        descent = fontMetrics.descent()

        # Text
        text = self.__headText + self.__commandText
        xpos = 0
        ypos = (height + ascent - descent) / 2
        painter.drawText(xpos, ypos, text)

        # Cursor
        if self.__cursorState:
            xpos = fontMetrics.horizontalAdvance(text) + 1
            ypos = 0
            width = 5
            painter.fillRect(QtCore.QRect(xpos, ypos, width, height), QtGui.QColor('#e8e8d3'))

        painter.end()


class ModeMarker(QtWidgets.QWidget):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.__mode = Modes.NORMAL
        self.__pixmap = {}
        self.__pixmap[Modes.NORMAL] = QtGui.QPixmap('img:normal.png')
        self.__pixmap[Modes.INSERT] = QtGui.QPixmap('img:insert.png')
        self.__pixmap[Modes.INSERT_LINE] = QtGui.QPixmap('img:insert_line.png')
        self.__pixmap[Modes.VISUAL] = QtGui.QPixmap('img:visual.png')
        self.__pixmap[Modes.VISUAL_LINE] = QtGui.QPixmap('img:visual_line.png')

    @Slot()
    def setMode(self, mode:Modes):
        self.__mode = mode
        self.update()

    @override
    def sizeHint(self):
        return QtCore.QSize(50, 12)

    @override
    def paintEvent(self, event):
        rect = self.rect()
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.__pixmap[self.__mode])
        painter.end()


class SheetStatusBar(QtWidgets.QWidget):

    # Signals
    commandEntered = Signal(str)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.__modeMarker = ModeMarker()
        self.__commandInput = CommandInput()
        self.__commandInput.commandEntered.connect(self.commandEntered.emit)

        hboxlayout = QtWidgets.QHBoxLayout(self)
        hboxlayout.addWidget(self.__modeMarker)
        hboxlayout.addWidget(self.__commandInput)
        hboxlayout.addStretch()
        hboxlayout.setContentsMargins(0, 0, 0, 0)

    @Slot()
    def receiveMode(self, mode:Modes):
        self.__modeMarker.setMode(mode)

    @Slot()
    def enterInputMode(self):
        self.__commandInput.setFocus()

