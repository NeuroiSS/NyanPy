from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import os
import sys

class ColorButton(QtWidgets.QPushButton):

    # Signal
    colorChanged = Signal(QtGui.QColor)

    def __init__(self, color = '#000000', parent = None):
        super().__init__(parent)
        self.__color = QtGui.QColor(color)
        self.clicked.connect(self.clickedEvent)

    @override
    def sizeHint(self):
        return QtCore.QSize(100, 18)

    @override
    def paintEvent(self, event):
        rect = self.rect()
        color = self.__color
        hexRgb = color.name(QtGui.QColor.HexRgb)

        painter = QtGui.QPainter(self)
        painter.fillRect(rect, color)
        
        painter.setPen(QtGui.QColor(Qt.white if color.lightnessF() < 0.6 else Qt.black))
        painter.setFont(QtWidgets.QApplication.font())
        fontMetrics = painter.fontMetrics()
        height = rect.height()
        width = rect.width()
        ascent = fontMetrics.ascent()
        descent = fontMetrics.descent()

        xpos = (width - fontMetrics.horizontalAdvance(hexRgb)) / 2
        ypos = (height + ascent - descent) / 2
        painter.drawText(xpos, ypos, hexRgb)
        painter.end()

    def color(self):
        return self.__color

    def setColor(self, color):
        self.__color = QtGui.QColor(color)
        self.update()

    def clickedEvent(self):
        color = QtWidgets.QColorDialog.getColor(Qt.white, self)
        if not color.isValid():
            return

        self.setColor(color)
        self.colorChanged.emit(color)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = ColorButton()
    ex.show()
    sys.exit(app.exec())

