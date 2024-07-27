from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys
import os

from DataListItemModule import Axes, Visibility
from GraphPropertiesModule import RangeOptions, GraphProperties

class GraphPropertiesWidget(QtWidgets.QWidget):

    # Signals
    valueUpdated = Signal()

    def __init__(self, parent = None):
        super().__init__(parent)
        self.__graphProperties = GraphProperties()

        # UI controls
        self.__lineEdit_Title = QtWidgets.QLineEdit()
        self.__lineEdit_XLabel = QtWidgets.QLineEdit()
        self.__lineEdit_LeftYLabel = QtWidgets.QLineEdit()
        self.__lineEdit_RightYLabel = QtWidgets.QLineEdit()
        self.__comboBox_XRange = QtWidgets.QComboBox()
        self.__lineEdit_XMin = QtWidgets.QLineEdit()
        self.__lineEdit_XMax = QtWidgets.QLineEdit()
        self.__comboBox_LeftYRange = QtWidgets.QComboBox()
        self.__lineEdit_LeftYMin = QtWidgets.QLineEdit()
        self.__lineEdit_LeftYMax = QtWidgets.QLineEdit()
        self.__comboBox_RightYRange = QtWidgets.QComboBox()
        self.__lineEdit_RightYMin = QtWidgets.QLineEdit()
        self.__lineEdit_RightYMax = QtWidgets.QLineEdit()
        self.__comboBox_LegendVisibility = QtWidgets.QComboBox()
        self.__spinBox_LegendPosX = QtWidgets.QSpinBox()
        self.__spinBox_LegendPosY = QtWidgets.QSpinBox()
        self.__spinBox_LegendColumnCount = QtWidgets.QSpinBox()
        self.__comboBox_GridVisibility = QtWidgets.QComboBox()
        self.__spinBox_GridOpacity = QtWidgets.QSpinBox()
        self.__spinBox_MarginLeft = QtWidgets.QSpinBox()
        self.__spinBox_MarginTop = QtWidgets.QSpinBox()
        self.__spinBox_MarginRight = QtWidgets.QSpinBox()
        self.__spinBox_MarginBottom = QtWidgets.QSpinBox()
        self.__spinBox_Width = QtWidgets.QSpinBox()
        self.__spinBox_Height = QtWidgets.QSpinBox()

        self.setupUi()
        self.connectSignals()

    def graphProperties(self):
        return self.__graphProperties

    def updateGraphProperties(self):
        # Set graph properties from UI controls
        self.__graphProperties.setTitle(self.__lineEdit_Title.text())
        self.__graphProperties.setLabel(Axes.X, self.__lineEdit_XLabel.text())
        self.__graphProperties.setLabel(Axes.LEFT_Y, self.__lineEdit_LeftYLabel.text())
        self.__graphProperties.setLabel(Axes.RIGHT_Y, self.__lineEdit_RightYLabel.text())
        self.__graphProperties.setRangeOption(Axes.X, RangeOptions(self.__comboBox_XRange.currentText()))
        self.__graphProperties.setRange(Axes.X, self.__lineEdit_XMin.text(), self.__lineEdit_XMax.text())
        self.__graphProperties.setRangeOption(Axes.LEFT_Y, RangeOptions(self.__comboBox_LeftYRange.currentText()))
        self.__graphProperties.setRange(Axes.LEFT_Y, self.__lineEdit_LeftYMin.text(), self.__lineEdit_LeftYMax.text())
        self.__graphProperties.setRangeOption(Axes.RIGHT_Y, RangeOptions(self.__comboBox_RightYRange.currentText()))
        self.__graphProperties.setRange(Axes.RIGHT_Y, self.__lineEdit_RightYMin.text(), self.__lineEdit_RightYMax.text())
        self.__graphProperties.setLegendVisibility(Visibility(self.__comboBox_LegendVisibility.currentText()))
        self.__graphProperties.setLegendPosX(self.__spinBox_LegendPosX.value())
        self.__graphProperties.setLegendPosY(self.__spinBox_LegendPosY.value())
        self.__graphProperties.setLegendColumnCount(self.__spinBox_LegendColumnCount.value())
        self.__graphProperties.setGridVisibility(Visibility(self.__comboBox_GridVisibility.currentText()))
        self.__graphProperties.setGridOpacity(self.__spinBox_GridOpacity.value())
        self.__graphProperties.setContentsMargins(\
                self.__spinBox_MarginLeft.value(), self.__spinBox_MarginTop.value(),\
                self.__spinBox_MarginRight.value(), self.__spinBox_MarginBottom.value())
        self.__graphProperties.setWidth(self.__spinBox_Width.value())
        self.__graphProperties.setHeight(self.__spinBox_Height.value())

        # Emit signal
        self.valueUpdated.emit()

    @staticmethod
    def addWidget(gridlayout, row:int, col:int, labelText:str, widget) -> int:
        gridlayout.addWidget(QtWidgets.QLabel(labelText), row, col)
        gridlayout.addWidget(widget, row, col + 1)
        return row + 1
    
    def setupUi(self):
        # ComboBox
        self.__comboBox_XRange.addItems([item.value for item in RangeOptions])
        self.__comboBox_LeftYRange.addItems([item.value for item in RangeOptions])
        self.__comboBox_RightYRange.addItems([item.value for item in RangeOptions])
        self.__comboBox_LegendVisibility.addItems([item.value for item in Visibility])
        self.__comboBox_GridVisibility.addItems([item.value for item in Visibility])

        # SpinBox ranges
        self.__spinBox_LegendPosX.setRange(0, 1000)
        self.__spinBox_LegendPosY.setRange(0, 1000)
        self.__spinBox_LegendColumnCount.setRange(1, 10)
        self.__spinBox_GridOpacity.setRange(0, 255)
        self.__spinBox_MarginLeft.setRange(0, 500)
        self.__spinBox_MarginTop.setRange(0, 500)
        self.__spinBox_MarginRight.setRange(0, 500)
        self.__spinBox_MarginBottom.setRange(0, 500)
        self.__spinBox_Width.setRange(200, 1000)
        self.__spinBox_Height.setRange(200, 1000)

        # SpinBox steps
        self.__spinBox_LegendPosX.setSingleStep(5)
        self.__spinBox_LegendPosY.setSingleStep(5)
        self.__spinBox_GridOpacity.setSingleStep(5)
        self.__spinBox_MarginLeft.setSingleStep(5)
        self.__spinBox_MarginTop.setSingleStep(5)
        self.__spinBox_MarginRight.setSingleStep(5)
        self.__spinBox_MarginBottom.setSingleStep(5)
        self.__spinBox_Width.setSingleStep(5)
        self.__spinBox_Height.setSingleStep(5)

        # LineEdit validator
        validator = QtGui.QRegularExpressionValidator(r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)', self)
        self.__lineEdit_XMin.setValidator(validator)
        self.__lineEdit_XMax.setValidator(validator)
        self.__lineEdit_LeftYMin.setValidator(validator)
        self.__lineEdit_LeftYMax.setValidator(validator)
        self.__lineEdit_RightYMin.setValidator(validator)
        self.__lineEdit_RightYMax.setValidator(validator)

        # Initial values
        self.__lineEdit_Title.setText(self.__graphProperties.title())
        self.__lineEdit_XLabel.setText(self.__graphProperties.label(Axes.X))
        self.__lineEdit_LeftYLabel.setText(self.__graphProperties.label(Axes.LEFT_Y))
        self.__lineEdit_RightYLabel.setText(self.__graphProperties.label(Axes.RIGHT_Y))
        self.__comboBox_XRange.setCurrentText(self.__graphProperties.rangeOption(Axes.X).value)
        self.__comboBox_LeftYRange.setCurrentText(self.__graphProperties.rangeOption(Axes.LEFT_Y).value)
        self.__comboBox_RightYRange.setCurrentText(self.__graphProperties.rangeOption(Axes.RIGHT_Y).value)
        self.__comboBox_LegendVisibility.setCurrentText(self.__graphProperties.legendVisibility().value)
        self.__spinBox_LegendPosX.setValue(self.__graphProperties.legendPosX())
        self.__spinBox_LegendPosY.setValue(self.__graphProperties.legendPosY())
        self.__spinBox_LegendColumnCount.setValue(self.__graphProperties.legendColumnCount())
        self.__comboBox_GridVisibility.setCurrentText(self.__graphProperties.gridVisibility().value)
        self.__spinBox_GridOpacity.setValue(self.__graphProperties.gridOpacity())

        left, top, right, bottom = self.__graphProperties.contentsMargins()
        self.__spinBox_MarginLeft.setValue(left)
        self.__spinBox_MarginTop.setValue(top)
        self.__spinBox_MarginRight.setValue(right)
        self.__spinBox_MarginBottom.setValue(bottom)
        self.__spinBox_Width.setValue(self.__graphProperties.width())
        self.__spinBox_Height.setValue(self.__graphProperties.height())

        # Layout
        gridlayout = QtWidgets.QGridLayout()
        row = 0
        col = 0
        row = self.addWidget(gridlayout, row, col, 'Title:', self.__lineEdit_Title)
        row = self.addWidget(gridlayout, row, col, 'X label:', self.__lineEdit_XLabel)
        row = self.addWidget(gridlayout, row, col, 'Left Y label:', self.__lineEdit_LeftYLabel)
        row = self.addWidget(gridlayout, row, col, 'Right Y label:', self.__lineEdit_RightYLabel)
        row = self.addWidget(gridlayout, row, col, 'X range:', self.__comboBox_XRange)
        row = self.addWidget(gridlayout, row, col, 'Min:', self.__lineEdit_XMin)
        row = self.addWidget(gridlayout, row, col, 'Max:', self.__lineEdit_XMax)
        row = self.addWidget(gridlayout, row, col, 'Left Y range:', self.__comboBox_LeftYRange)
        row = self.addWidget(gridlayout, row, col, 'Min:', self.__lineEdit_LeftYMin)
        row = self.addWidget(gridlayout, row, col, 'Max:', self.__lineEdit_LeftYMax)
        row = self.addWidget(gridlayout, row, col, 'Right Y range:', self.__comboBox_RightYRange)
        row = self.addWidget(gridlayout, row, col, 'Min:', self.__lineEdit_RightYMin)
        row = self.addWidget(gridlayout, row, col, 'Max:', self.__lineEdit_RightYMax)
        row = 0
        col = 2
        row = self.addWidget(gridlayout, row, col, 'Legend visibility:', self.__comboBox_LegendVisibility)
        row = self.addWidget(gridlayout, row, col, 'Legend pos X:', self.__spinBox_LegendPosX)
        row = self.addWidget(gridlayout, row, col, 'Legend pos Y:', self.__spinBox_LegendPosY)
        row = self.addWidget(gridlayout, row, col, 'Column count:', self.__spinBox_LegendColumnCount)
        row = self.addWidget(gridlayout, row, col, 'Grid visibility:', self.__comboBox_GridVisibility)
        row = self.addWidget(gridlayout, row, col, 'Grid opacity:', self.__spinBox_GridOpacity)
        row = self.addWidget(gridlayout, row, col, 'Margin left:', self.__spinBox_MarginLeft)
        row = self.addWidget(gridlayout, row, col, 'Margin top:', self.__spinBox_MarginTop)
        row = self.addWidget(gridlayout, row, col, 'Margin right:', self.__spinBox_MarginRight)
        row = self.addWidget(gridlayout, row, col, 'Margin bottom:', self.__spinBox_MarginBottom)
        row = self.addWidget(gridlayout, row, col, 'Width:', self.__spinBox_Width)
        row = self.addWidget(gridlayout, row, col, 'Height:', self.__spinBox_Height)

        gridlayout.setRowStretch(99, 1)
        gridlayout.setColumnStretch(1, 1)
        gridlayout.setColumnStretch(3, 1)
        gridlayout.setSpacing(5)
        self.setLayout(gridlayout)

    def connectSignals(self):
        self.__lineEdit_Title.textChanged.connect(self.updateGraphProperties)
        self.__lineEdit_XLabel.textChanged.connect(self.updateGraphProperties)
        self.__lineEdit_LeftYLabel.textChanged.connect(self.updateGraphProperties)
        self.__lineEdit_RightYLabel.textChanged.connect(self.updateGraphProperties)
        self.__comboBox_XRange.currentIndexChanged.connect(self.updateGraphProperties)
        self.__lineEdit_XMin.textChanged.connect(self.updateGraphProperties)
        self.__lineEdit_XMax.textChanged.connect(self.updateGraphProperties)
        self.__comboBox_LeftYRange.currentIndexChanged.connect(self.updateGraphProperties)
        self.__lineEdit_LeftYMin.textChanged.connect(self.updateGraphProperties)
        self.__lineEdit_LeftYMax.textChanged.connect(self.updateGraphProperties)
        self.__comboBox_RightYRange.currentIndexChanged.connect(self.updateGraphProperties)
        self.__lineEdit_RightYMin.textChanged.connect(self.updateGraphProperties)
        self.__lineEdit_RightYMax.textChanged.connect(self.updateGraphProperties)
        self.__comboBox_LegendVisibility.currentIndexChanged.connect(self.updateGraphProperties)
        self.__spinBox_LegendPosX.valueChanged.connect(self.updateGraphProperties)
        self.__spinBox_LegendPosY.valueChanged.connect(self.updateGraphProperties)
        self.__spinBox_LegendColumnCount.valueChanged.connect(self.updateGraphProperties)
        self.__comboBox_GridVisibility.currentIndexChanged.connect(self.updateGraphProperties)
        self.__spinBox_GridOpacity.valueChanged.connect(self.updateGraphProperties)
        self.__spinBox_MarginLeft.valueChanged.connect(self.updateGraphProperties)
        self.__spinBox_MarginTop.valueChanged.connect(self.updateGraphProperties)
        self.__spinBox_MarginRight.valueChanged.connect(self.updateGraphProperties)
        self.__spinBox_MarginBottom.valueChanged.connect(self.updateGraphProperties)
        self.__spinBox_Width.valueChanged.connect(self.updateGraphProperties)
        self.__spinBox_Height.valueChanged.connect(self.updateGraphProperties)

