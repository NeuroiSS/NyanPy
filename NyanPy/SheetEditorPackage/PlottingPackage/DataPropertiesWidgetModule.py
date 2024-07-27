from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys
import os

from ColorButtonModule import ColorButton
from DataListItemModule import *
from DataEditorModule import DataEditor

class DataPropertiesWidget(QtWidgets.QWidget):

    # Signals
    valueUpdated = Signal()

    paletteColors = {\
        'default':'#9400d3 #009e73 #56b4e9 #e69f00 #f0e442 #0072b2 #e51e10 #000000',\
        'classic':'#ff0000 #00ff00 #0000ff #ff00ff #00ffff #ffff00 #000000 #ff4c00 #a0a0a4',\
        'podo'   :'#000000 #e69f00 #56b4e9 #009e73 #f0e442 #0072b2 #d55e00 #cc79a7',\
        'gem'    :'#0072bd #d95319 #edb120 #7e2f8e #77ac30 #4dbeee #a2142f',\
        'gem12'  :'#0072bd #d95319 #edb120 #7e2f8e #77ac30 #4dbeee #a2142f #ffd60a #6582fd #ff453a #00a3a3 #cb845d',\
        'glow'   :'#268cdd #f57729 #ffe864 #c05cfb #49db40 #6cf4ff #f267c5',\
        'gloleftWidget2' :'#268cdd #f57729 #ffe864 #c05cfb #49db40 #6cf4ff #f267c5 #fec04c #7da9ff #ff7a74 #1fcfbe #dc996c',\
        'sail'   :'#104280 #54b6ff #ff453a #902622 #1171be',\
        'reef'   :'#dd5400 #54b6ff #1171be #fe9043 #74ebda #00a3a3',\
        'meadow' :'#02580e #3ac831 #ffd60a #f57729 #c04c0b #fa8ad4 #7da9ff',\
        'dye'    :'#b7312c #3baa32 #5e2296 #1171be #dd5400 #027880 #e951b8',\
        'earth'  :'#104280 #b7312c #9c7720 #02580e #dc996c #5f1b08 #ffd19e'}

    def __init__(self, parent = None):
        super().__init__(parent)
        self.__currentDataListItem = DataListItem()

        # UI controls
        self.__listWidget_DataList = QtWidgets.QListWidget()
        self.__pushButton_Edit = QtWidgets.QPushButton('Edit')
        self.__pushButton_Delete = QtWidgets.QPushButton('Delete')
        self.__pushButton_Up = QtWidgets.QPushButton('Up')
        self.__pushButton_Down = QtWidgets.QPushButton('Down')

        self.__lineEdit_DataName = QtWidgets.QLineEdit()
        self.__comboBox_LineStyle = QtWidgets.QComboBox()
        self.__spinBox_LineWidth = QtWidgets.QSpinBox()
        self.__comboBox_LineColorOption = QtWidgets.QComboBox()
        self.__comboBox_PaletteName = QtWidgets.QComboBox()
        self.__colorButton_CustomColor = ColorButton()
        self.__comboBox_SymbolStyle = QtWidgets.QComboBox()
        self.__spinBox_SymbolSize = QtWidgets.QSpinBox()
        self.__comboBox_SymbolFill = QtWidgets.QComboBox()
        self.__lineEdit_LegendText = QtWidgets.QLineEdit()
        self.__comboBox_YAxis = QtWidgets.QComboBox()
        self.__comboBox_Visibility = QtWidgets.QComboBox()

        self.setupUi()
        self.connectSignals()

    def colorOrder(self) -> list:
        paletteName = self.__comboBox_PaletteName.currentText()
        colorOrder = self.paletteColors[paletteName]
        colorOrder = colorOrder.split()
        return colorOrder
    
    def listItems(self) -> list:
        return [self.__listWidget_DataList.item(row) for row in range(self.__listWidget_DataList.count())]

    @Slot()
    def receiveDataListItems(self, items):
        for item in items:
            self.__listWidget_DataList.addItem(item)

    def blockUiControlSignals(self, state):
        self.__lineEdit_DataName.blockSignals(state)
        self.__comboBox_LineStyle.blockSignals(state)
        self.__spinBox_LineWidth.blockSignals(state)
        self.__comboBox_LineColorOption.blockSignals(state)
        self.__colorButton_CustomColor.blockSignals(state)
        self.__comboBox_SymbolStyle.blockSignals(state)
        self.__spinBox_SymbolSize.blockSignals(state)
        self.__comboBox_SymbolFill.blockSignals(state)
        self.__lineEdit_LegendText.blockSignals(state)
        self.__comboBox_YAxis.blockSignals(state)
        self.__comboBox_Visibility.blockSignals(state)

    @Slot()
    def updateUiControlValues(self):
        # Disable UI control signals
        self.blockUiControlSignals(True)

        # Set values to UI controls values
        self.__lineEdit_DataName.setText(self.__currentDataListItem.text())
        self.__comboBox_LineStyle.setCurrentText(self.__currentDataListItem.lineStyle().value)
        self.__spinBox_LineWidth.setValue(self.__currentDataListItem.lineWidth())
        self.__comboBox_LineColorOption.setCurrentText(self.__currentDataListItem.lineColorOption().value)
        self.__colorButton_CustomColor.setColor(self.__currentDataListItem.customColor())
        self.__comboBox_SymbolStyle.setCurrentText(self.__currentDataListItem.symbolStyle().value)
        self.__spinBox_SymbolSize.setValue(self.__currentDataListItem.symbolSize())
        self.__comboBox_SymbolFill.setCurrentText(self.__currentDataListItem.symbolFill().value)
        self.__lineEdit_LegendText.setText(self.__currentDataListItem.legendText())
        self.__comboBox_YAxis.setCurrentText(self.__currentDataListItem.yaxis().value)
        self.__comboBox_Visibility.setCurrentText(self.__currentDataListItem.visibility().value)

        # Enable UI control signals
        self.blockUiControlSignals(False)

    @Slot()
    def updateDataListItemValues(self):
        # Set current DataListItem values from UI controls
        self.__currentDataListItem.setText(self.__lineEdit_DataName.text())
        self.__currentDataListItem.setLineStyle(LineStyles(self.__comboBox_LineStyle.currentText()))
        self.__currentDataListItem.setLineWidth(self.__spinBox_LineWidth.value())
        self.__currentDataListItem.setLineColorOption(LineColorOptions(self.__comboBox_LineColorOption.currentText()))
        self.__currentDataListItem.setCustomColor(self.__colorButton_CustomColor.color())
        self.__currentDataListItem.setSymbolStyle(SymbolStyles(self.__comboBox_SymbolStyle.currentText()))
        self.__currentDataListItem.setSymbolSize(self.__spinBox_SymbolSize.value())
        self.__currentDataListItem.setSymbolFill(SymbolFill(self.__comboBox_SymbolFill.currentText()))
        self.__currentDataListItem.setLegendText(self.__lineEdit_LegendText.text())
        self.__currentDataListItem.setYAxis(Axes(self.__comboBox_YAxis.currentText()))
        self.__currentDataListItem.setVisibility(Visibility(self.__comboBox_Visibility.currentText()))

        # Emit signal
        self.valueUpdated.emit()

    @Slot()
    def currentDataListItemChanged(self):
        selected = self.__listWidget_DataList.selectedItems()
        self.__currentDataListItem = selected[0] if selected else DataListItem()
        self.updateUiControlValues()

    @Slot()
    def edit(self):
        selected = self.__listWidget_DataList.selectedItems()
        if not selected:
            return

        dataEditor = DataEditor(selected[0], self)
        dataEditor.exec()

    @Slot()
    def delete(self):
        selected = self.__listWidget_DataList.selectedItems()
        if not selected:
            return

        row = self.__listWidget_DataList.row(selected[0])
        self.__listWidget_DataList.takeItem(row)

    @Slot()
    def moveUp(self):
        selected = self.__listWidget_DataList.selectedItems()
        if not selected:
            return

        row = self.__listWidget_DataList.row(selected[0])
        if row > 0:
            currentItem = self.__listWidget_DataList.takeItem(row)
            self.__listWidget_DataList.insertItem(row - 1, currentItem)

            # Cursor
            currentIndex = self.__listWidget_DataList.indexFromItem(currentItem)
            self.__listWidget_DataList.setCurrentIndex(currentIndex)

    @Slot()
    def moveDown(self):
        selected = self.__listWidget_DataList.selectedItems()
        if not selected:
            return

        row = self.__listWidget_DataList.row(selected[0])
        if row < self.__listWidget_DataList.count() - 1:
            currentItem = self.__listWidget_DataList.takeItem(row)
            self.__listWidget_DataList.insertItem(row + 1, currentItem)

            # Cursor
            currentIndex = self.__listWidget_DataList.indexFromItem(currentItem)
            self.__listWidget_DataList.setCurrentIndex(currentIndex)
    
    def connectSignals(self):
        # ListWidget
        self.__listWidget_DataList.itemSelectionChanged.connect(self.currentDataListItemChanged)
        self.__listWidget_DataList.itemDoubleClicked.connect(self.edit)

        # Buttons
        self.__pushButton_Edit.clicked.connect(self.edit)
        self.__pushButton_Delete.clicked.connect(self.delete)
        self.__pushButton_Up.clicked.connect(self.moveUp)
        self.__pushButton_Down.clicked.connect(self.moveDown)

        # UI controls
        self.__lineEdit_DataName.textChanged.connect(self.updateDataListItemValues)
        self.__comboBox_LineStyle.currentIndexChanged.connect(self.updateDataListItemValues)
        self.__spinBox_LineWidth.valueChanged.connect(self.updateDataListItemValues)
        self.__comboBox_LineColorOption.currentIndexChanged.connect(self.updateDataListItemValues)
        self.__comboBox_PaletteName.currentIndexChanged.connect(self.updateDataListItemValues)
        self.__colorButton_CustomColor.colorChanged.connect(self.updateDataListItemValues)
        self.__comboBox_SymbolStyle.currentIndexChanged.connect(self.updateDataListItemValues)
        self.__spinBox_SymbolSize.valueChanged.connect(self.updateDataListItemValues)
        self.__comboBox_SymbolFill.currentIndexChanged.connect(self.updateDataListItemValues)
        self.__lineEdit_LegendText.textChanged.connect(self.updateDataListItemValues)
        self.__comboBox_YAxis.currentIndexChanged.connect(self.updateDataListItemValues)
        self.__comboBox_Visibility.currentIndexChanged.connect(self.updateDataListItemValues)

    @staticmethod
    def addWidget(gridlayout, row:int, col:int, labelText:str, widget) -> int:
        gridlayout.addWidget(QtWidgets.QLabel(labelText), row, col)
        gridlayout.addWidget(widget, row, col + 1)
        return row + 1
    
    def setupUi(self):
        # Populate comboboxes
        self.__comboBox_LineStyle.addItems([item.value for item in LineStyles])
        self.__comboBox_LineColorOption.addItems([item.value for item in LineColorOptions])
        self.__comboBox_PaletteName.addItems([item for item in self.paletteColors])
        self.__comboBox_SymbolStyle.addItems([item.value for item in SymbolStyles])
        self.__comboBox_SymbolFill.addItems([item.value for item in SymbolFill])
        self.__comboBox_YAxis.addItems([Axes.LEFT_Y, Axes.RIGHT_Y])
        self.__comboBox_Visibility.addItems([item.value for item in Visibility])

        # Layout
        gridlayout1 = QtWidgets.QGridLayout()
        row = 0
        col = 0
        row = self.addWidget(gridlayout1, row, col, 'Data name:', self.__lineEdit_DataName)
        row = self.addWidget(gridlayout1, row, col, 'Line style:', self.__comboBox_LineStyle)
        row = self.addWidget(gridlayout1, row, col, 'Line width:', self.__spinBox_LineWidth)
        row = self.addWidget(gridlayout1, row, col, 'Line color option:', self.__comboBox_LineColorOption)
        row = self.addWidget(gridlayout1, row, col, 'Palette name:', self.__comboBox_PaletteName)
        row = self.addWidget(gridlayout1, row, col, 'Custom color:', self.__colorButton_CustomColor)
        row = self.addWidget(gridlayout1, row, col, 'Symbol style:', self.__comboBox_SymbolStyle)
        row = self.addWidget(gridlayout1, row, col, 'Symbol size:', self.__spinBox_SymbolSize)
        row = self.addWidget(gridlayout1, row, col, 'Symbol fill:', self.__comboBox_SymbolFill)
        row = self.addWidget(gridlayout1, row, col, 'Legend text:', self.__lineEdit_LegendText)
        row = self.addWidget(gridlayout1, row, col, 'Y axis:', self.__comboBox_YAxis)
        row = self.addWidget(gridlayout1, row, col, 'Visibility:', self.__comboBox_Visibility)
        gridlayout1.setRowStretch(99, 1)
        gridlayout1.setContentsMargins(0, 0, 0, 0)
        gridlayout1.setSpacing(5)
        rightWidget = QtWidgets.QWidget()
        rightWidget.setLayout(gridlayout1)

        gridlayout2 = QtWidgets.QGridLayout()
        gridlayout2.addWidget(self.__pushButton_Edit, 0, 0)
        gridlayout2.addWidget(self.__pushButton_Delete, 1, 0)
        gridlayout2.addWidget(self.__pushButton_Up, 0, 1)
        gridlayout2.addWidget(self.__pushButton_Down, 1, 1)
        gridlayout2.setSpacing(5)

        vboxlayout = QtWidgets.QVBoxLayout()
        vboxlayout.addWidget(self.__listWidget_DataList)
        vboxlayout.addLayout(gridlayout2)
        vboxlayout.setContentsMargins(0, 0, 0, 0)
        leftWidget = QtWidgets.QWidget()
        leftWidget.setLayout(vboxlayout)

        splitter = QtWidgets.QSplitter(Qt.Horizontal)
        splitter.addWidget(leftWidget)
        splitter.addWidget(rightWidget)

        hboxlayout = QtWidgets.QHBoxLayout()
        hboxlayout.addWidget(splitter)
        self.setLayout(hboxlayout)

