from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
from enum import StrEnum

from DataListItemModule import Axes, Visibility

class RangeOptions(StrEnum):
    AUTO = 'auto'
    MANUAL = 'manual'

class GraphProperties(QtCore.QObject):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.__title = 'Title'
        self.__labels = {\
                Axes.X      : 'X Axis',\
                Axes.LEFT_Y : 'Y Axis',\
                Axes.RIGHT_Y: 'Y2 Axis' }
        self.__rangeOptions = {\
                Axes.X      : RangeOptions.AUTO,\
                Axes.LEFT_Y : RangeOptions.AUTO,\
                Axes.RIGHT_Y: RangeOptions.AUTO }
        self.__ranges = {\
                Axes.X      : (0.0, 1.0),\
                Axes.LEFT_Y : (0.0, 1.0),\
                Axes.RIGHT_Y: (0.0, 1.0) }
        self.__legendVisibility = Visibility.SHOW
        self.__legendPosX = 0
        self.__legendPosY = 0
        self.__legendColumnCount = 1
        self.__gridVisibility = Visibility.SHOW
        self.__gridOpacity = 20
        self.__contentsMargins = (0, 0, 0, 0) # left,top,right,bottom 
        self.__width = 500
        self.__height = 300

    def title(self) -> str:
        return self.__title

    def label(self, axis:Axes) -> str:
        return self.__labels[axis]

    def rangeOption(self, axis:Axes) -> RangeOptions:
        return self.__rangeOptions[axis]

    def range(self, axis:Axes) -> tuple:
        return self.__ranges[axis]

    def legendVisibility(self) -> Visibility:
        return self.__legendVisibility

    def legendPosX(self) -> int:
        return self.__legendPosX

    def legendPosY(self) -> int:
        return self.__legendPosY

    def legendPosition(self) -> tuple:
        return (self.__legendPosX, self.__legendPosY)

    def legendColumnCount(self) -> int:
        return self.__legendColumnCount

    def gridVisibility(self) -> Visibility:
        return self.__gridVisibility

    def gridOpacity(self) -> int:
        return self.__gridOpacity

    def contentsMargins(self) -> tuple:
        return self.__contentsMargins

    def width(self) -> int:
        return self.__width

    def height(self) -> int:
        return self.__height

    def setTitle(self, title:str):
        self.__title = title

    def setLabel(self, axis:Axes, label:str):
        self.__labels[axis] = label

    def setRangeOption(self, axis:Axes, rangeOption:RangeOptions):
        self.__rangeOptions[axis] = rangeOption

    def setRange(self, axis:Axes, min_, max_):
        try:
            min_ = float(min_)
        except Exception:
            min_ = 0.0
        try:
            max_ = float(max_)
        except Exception:
            max_ = 1.0

        if min_ >= max_:
            min_, max_ = 0.0, 1.0
        self.__ranges[axis] = (min_, max_)

    def setLegendVisibility(self, visibility:Visibility):
        self.__legendVisibility = visibility

    def setLegendPosX(self, posX:int):
        self.__legendPosX = posX

    def setLegendPosY(self, posY:int):
        self.__legendPosY = posY

    def setLegendColumnCount(self, count:int):
        self.__legendColumnCount = count

    def setGridVisibility(self, visibility:Visibility):
        self.__gridVisibility = visibility

    def setGridOpacity(self, gridOpacity:int):
        self.__gridOpacity = gridOpacity

    def setContentsMargins(self, left:int, top:int, right:int, bottom:int):
        self.__contentsMargins = (left, top, right, bottom)

    def setWidth(self, width:int):
        self.__width = width

    def setHeight(self, height:int):
        self.__height = height

