from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
from enum import StrEnum

class LineStyles(StrEnum):
    NONE = 'none'
    SOLID_LINE = 'solid line'
    DASH_LINE = 'dash line'
    DOT_LINE = 'dot line'
    DASH_DOT_LINE = 'dash-dot line'
    DASH_DOT_DOT_LINE = 'dash-dot-dot line'

class LineColorOptions(StrEnum):
    PALETTE_COLOR = 'palette color'
    CUSTOM_COLOR = 'custom color'

class SymbolStyles(StrEnum):
    NONE = 'none'
    CIRCLE = 'circle'
    SQUARE = 'square'
    TRIANGLE = 'triangle'
    DIAMOND = 'diamond'
    PLUS = 'plus'
    TRIANGLE_UP = 'triangle up'
    TRIANGLE_RIGHT = 'triangle right'
    TRIANGLE_LEFT = 'triangle left'
    PENTAGON = 'pentagon'
    HEXAGON = 'hexagon'
    STAR = 'star'
    VERTICAL_LINE = 'vertical line'
    HORIZONTAL_LINE = 'horizontal line'
    CROSS = 'cross'
    ARROW_UP = 'arrow up'
    ARROW_RIGHT = 'arrow right'
    ARROW_DOWN = 'arrow down'
    ARROW_LEFT = 'arrow left'
    CROSSHAIR = 'crosshair'

class SymbolFill(StrEnum):
    UNFILLED = 'unfilled'
    FILLED = 'filled'

class Axes(StrEnum):
    X  = 'x axis'
    LEFT_Y  = 'left y axis'
    RIGHT_Y = 'right y axis'

class Visibility(StrEnum):
    SHOW = 'show'
    HIDE = 'hide'

class DataListItem(QtWidgets.QListWidgetItem):

    def __init__(self, text = '', parent = None):
        super().__init__(text, parent)
        self.__x = []
        self.__y = []
        self.__lineStyle = LineStyles.SOLID_LINE
        self.__lineWidth = 2
        self.__lineColorOption = LineColorOptions.PALETTE_COLOR
        self.__customColor = '#000000'
        self.__symbolStyle = SymbolStyles.NONE
        self.__symbolSize = 7
        self.__symbolFill = SymbolFill.UNFILLED
        self.__legendText = ''
        self.__yaxis = Axes.LEFT_Y
        self.__visibility = Visibility.SHOW

    def x(self) -> list:
        return self.__x

    def y(self) -> list:
        return self.__y

    def lineStyle(self) -> LineStyles:
        return self.__lineStyle

    def lineWidth(self) -> int:
        return self.__lineWidth

    def lineColorOption(self) -> LineColorOptions:
        return self.__lineColorOption

    def customColor(self) -> str: # Hex RGB
        return self.__customColor

    def symbolStyle(self) -> SymbolStyles:
        return self.__symbolStyle

    def symbolSize(self) -> int:
        return self.__symbolSize

    def symbolFill(self) -> SymbolFill:
        return self.__symbolFill

    def legendText(self) -> str:
        return self.__legendText

    def yaxis(self) -> Axes:
        return self.__yaxis

    def visibility(self) -> Visibility:
        return self.__visibility

    def setX(self, x:list):
        self.__x = x.copy()

    def setY(self, y:list):
        self.__y = y.copy()

    def setLineStyle(self, lineStyle:LineStyles):
        self.__lineStyle = lineStyle

    def setLineWidth(self, lineWidth:int):
        self.__lineWidth = lineWidth

    def setLineColorOption(self, lineColorOption:LineColorOptions):
        self.__lineColorOption = lineColorOption

    def setCustomColor(self, customColor:str): # Hex RGB
        self.__customColor = customColor

    def setSymbolStyle(self, symbolStyle:SymbolStyles):
        self.__symbolStyle = symbolStyle

    def setSymbolSize(self, symbolSize:int):
        self.__symbolSize = symbolSize

    def setSymbolFill(self, symbolFill:SymbolFill):
        self.__symbolFill = symbolFill

    def setLegendText(self, legendText:str):
        self.__legendText = legendText

    def setYAxis(self, yaxis:Axes):
        self.__yaxis = yaxis

    def setVisibility(self, visibility:Visibility):
        self.__visibility = visibility

