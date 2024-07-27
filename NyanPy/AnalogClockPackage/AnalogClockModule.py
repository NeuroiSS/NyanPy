from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys
import os
import math

class AnalogClock(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.__time = QtCore.QTime.currentTime()
        self.__mpos = QtCore.QPoint()
        self.__staysOnTopAction = QtGui.QAction('Window Stays on Top')
        self.__staysOnTopAction.setCheckable(True)
        self.__staysOnTopAction.toggled.connect(self.toggleStaysOnTop)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenuEvent)
        self.resize(150, 150)
        self.setWindowTitle('Analog Clock')
        self.setStyleSheet('background-color: #151515')

        self.__timer = QtCore.QTimer(self)
        self.__timer.timeout.connect(self.checkUpdate)
        self.__timer.start(20)

    @Slot()
    def contextMenuEvent(self, pos:QtCore.QPoint):
        menu = QtWidgets.QMenu(self)
        menu.addAction(self.__staysOnTopAction)
        menu.exec(self.mapToGlobal(pos))

    @Slot()
    def toggleStaysOnTop(self, checked):
        flags = self.windowFlags()
        self.setWindowFlags(flags ^ Qt.WindowStaysOnTopHint)
        self.show()

    @override
    def mousePressEvent(self, event):
        self.__mpos = QtCore.QPoint(event.position().x(), event.position().y())

    @override
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            diff = QtCore.QPoint(event.position().x(), event.position().y()) - self.__mpos
            newpos = self.pos() + diff

            self.move(newpos)

    @Slot()
    def checkUpdate(self):
        time = QtCore.QTime.currentTime()
        if time.second() != self.__time.second():
            self.update()

        self.__time = time

    @override
    def paintEvent(self, event):
        hourHand   = [QtCore.QPoint(x, y) for (x, y) in [(4, 14), (-4, 14), (-2, -51), (2, -51)]]
        minuteHand = [QtCore.QPoint(x, y) for (x, y) in [(4, 14), (-4, 14), (-1, -89), (1, -89)]]
        secondHand = [QtCore.QPoint(x, y) for (x, y) in [(1, 14), (-1, 14), (-1, -89), (1, -89)]]

        faceColor   = QtGui.QColor('#e8e8d3')
        hourColor   = QtGui.QColor('#e8e8d3')
        minuteColor = QtGui.QColor('#fad07a')
        secondColor = QtGui.QColor('#cf6a4c')

        side = min(self.width(), self.height())

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(side / 200, side / 200)

        # Date and Time
        date = QtCore.QDate.currentDate()
        time = QtCore.QTime.currentTime()

        # Clock Face
        painter.setPen(Qt.NoPen)
        painter.setBrush(faceColor)
        for i in range(12):
            painter.drawRect(86, -2, 12, 4)
            painter.rotate(30)

        painter.setPen(faceColor)
        for i in range(60):
            painter.drawLine(92, 0, 96, 0)
            painter.rotate(6)

        painter.setFont(QtGui.QFont('Calibri', 20))
        for i in range(1, 13):
            xpos = 70 * math.sin(math.pi * (i / 6)) - painter.fontMetrics().horizontalAdvance(str(i)) / 2
            ypos = 70 * math.cos(math.pi * (i / 6)) - 9
            painter.drawText(xpos, -ypos, str(i))

        painter.setPen(faceColor)
        painter.setFont(QtGui.QFont('Calibri', 12))
        text = date.toString('MMM d yyyy')
        painter.drawText(-painter.fontMetrics().horizontalAdvance(text) / 2, -20, text)
        text = date.toString('ddd')
        painter.drawText(-painter.fontMetrics().horizontalAdvance(text) / 2, 40, text)

        # Hour
        painter.setPen(Qt.NoPen)
        painter.setBrush(hourColor)
        painter.save()
        painter.rotate(30 * (time.hour() + time.minute() / 60))
        painter.drawConvexPolygon(hourHand)
        painter.restore()

        # Minute
        painter.setPen(Qt.NoPen)
        painter.setBrush(minuteColor)
        painter.save()
        painter.rotate(6 * (time.minute() + time.second() / 60))
        painter.drawConvexPolygon(minuteHand)
        painter.restore()

        # Second
        painter.setPen(Qt.NoPen)
        painter.setBrush(secondColor)
        painter.save()
        painter.rotate(6 * time.second())
        painter.drawConvexPolygon(secondHand)
        painter.drawEllipse(-4, -4, 8, 8)
        painter.restore()

