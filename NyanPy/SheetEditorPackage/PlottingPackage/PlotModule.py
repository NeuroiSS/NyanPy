from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys
import os

from DataListItemModule import *
from GraphPropertiesModule import *

# PyQtGraph
import pyqtgraph as pg

# Global configuration options
#pg.setConfigOptions(antialias=True, background='w', foreground='k')

class Plot(pg.GraphicsLayoutWidget):

    styles = {'none': Qt.NoPen, 'solid line': Qt.SolidLine, 'dash line': Qt.DashLine,\
            'dot line': Qt.DotLine, 'dash-dot line': Qt.DashDotLine,\
            'dash-dot-dot line': Qt.DashDotDotLine}

    symbols = {'none': None, 'circle': 'o', 'square': 's', 'triangle': 't', 'diamond': 'd',\
            'plus': '+', 'triangle up': 't1', 'triangle right': 't2', 'triangle left': 't3',\
            'pentagon': 'p', 'hexagon': 'h', 'star': 'star', 'vertical line': '|',\
            'horizontal line': '_', 'cross': 'x', 'arrow up': 'arrow_up',\
            'arrow right': 'arrow_right', 'arrow down': 'arrow_down', 'arrow left': 'arrow_left',\
            'crosshair': 'crosshair'}

    def __init__(self, parent = None):
        super().__init__(parent)
        self.p1 = None
        self.p2 = None

        self.resize(200, 200)
        self.setWindowTitle('Plot')
        self.setWindowFlags(Qt.Tool | self.windowFlags())

    @Slot()
    def plot(self, items:list, colorOrder:list, properties):
        # Backup Global options
        foreground = pg.getConfigOption('foreground')
        antialias = pg.getConfigOption('antialias')

        # Set Global options and background color
        pg.setConfigOptions(antialias=True, foreground='k')
        self.setBackground('w')

        # Clear contents
        self.clear()
        self.p1 = None

        if self.p2:
            self.p2.clear()
            self.p2 = None

        # Resize
        self.resize(properties.width(), properties.height())

        # Title, Labels
        self.p1 = self.addPlot()
        self.p1.setTitle(properties.title() or None)
        self.p1.setLabels(bottom=properties.label(Axes.X), left=properties.label(Axes.LEFT_Y))

        # X axis range
        if properties.rangeOption(Axes.X) == RangeOptions.MANUAL:
            min_, max_ = properties.range(Axes.X)
            self.p1.setXRange(min_, max_, padding=0)

        # Left Y axis range
        if properties.rangeOption(Axes.LEFT_Y) == RangeOptions.MANUAL:
            min_, max_ = properties.range(Axes.LEFT_Y)
            self.p1.setYRange(min_, max_, padding=0)

        # Check plot on the right Y axis
        plotOnRight = False
        for item in items:
            if item.yaxis() == Axes.RIGHT_Y and item.visibility() == Visibility.SHOW:
                plotOnRight = True
                break

        # Right Y axis
        self.p2 = pg.ViewBox()
        if plotOnRight:
            self.p1.showAxis('right')
            self.p1.scene().addItem(self.p2)
            self.p1.getAxis('right').linkToView(self.p2)
            self.p2.setXLink(self.p1)
            self.p1.getAxis('right').setLabel(properties.label(Axes.RIGHT_Y))

            # X and RIGHT_Y axis ranges
            if properties.rangeOption(Axes.X) == RangeOptions.MANUAL:
                min_, max_ = properties.range(Axes.X)
                self.p2.setXRange(min_, max_, padding=0)

            if properties.rangeOption(Axes.RIGHT_Y) == RangeOptions.MANUAL:
                min_, max_ = properties.range(Axes.RIGHT_Y)
                self.p2.setYRange(min_, max_, padding=0)

        # Grid
        if properties.gridVisibility() == Visibility.SHOW:
            opacity = properties.gridOpacity()
            self.p1.getAxis('left').setGrid(opacity)
            self.p1.getAxis('bottom').setGrid(opacity)

        # Legend
        legend = pg.LegendItem()
        if properties.legendVisibility() == Visibility.SHOW:
            legend.setParentItem(self.p1)
            posX, posY = properties.legendPosition()
            legend.setOffset((posX + 1, posY + 1))
            legend.setColumnCount(properties.legendColumnCount())

        # Margins
        left, top, right, bottom = properties.contentsMargins()
        self.p1.layout.setContentsMargins(left, top, right, bottom)

        # Plot
        for index, item in enumerate(items):
            if item.visibility() == Visibility.HIDE:
                continue
            x = item.x()
            y = item.y()
            name = item.legendText()
            color = colorOrder[index % len(colorOrder)]\
                    if item.lineColorOption() == LineColorOptions.PALETTE_COLOR\
                    else item.customColor()
            style = self.styles[item.lineStyle().value]
            pen = pg.mkPen(color=color, style=style, width=item.lineWidth())
            symbol = self.symbols[item.symbolStyle().value]
            symbolSize = item.symbolSize()
            symbolPen = color
            symbolBrush = color if item.symbolFill() == SymbolFill.FILLED else None

            plotDataItem = pg.PlotDataItem(x, y, name=name, pen=pen, symbol=symbol,\
                    symbolSize=symbolSize, symbolPen=symbolPen, symbolBrush=symbolBrush)

            plotItem = self.p1 if item.yaxis() == Axes.LEFT_Y else self.p2
            plotItem.addItem(plotDataItem)
            if properties.legendVisibility() == Visibility.SHOW and name:
                legend.addItem(plotDataItem, name)

        self.updateViews()
        self.p1.vb.sigResized.connect(self.updateViews)

        # Reset Global options
        pg.setConfigOptions(antialias=antialias, foreground=foreground)

    @Slot()
    def updateViews(self):
        if not self.p1 or not self.p2:
            return

        self.p2.setGeometry(self.p1.vb.sceneBoundingRect())
        self.p2.linkedViewChanged(self.p1.vb, self.p2.XAxis)

