from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
import numpy
import re

class VariableItem(QtCore.QObject):

    def __init__(self, name, value, description = '', parent = None):
        super().__init__(parent)
        self.__name = name
        self.__value = value
        self.__evalValue = None
        self.__description = description

    def name(self):
        return self.__name

    def value(self):
        return self.__value

    def description(self):
        return self.__description

    def evalValue(self):
        return self.__evalValue

    def evalType(self) -> str:
        x = self.__evalValue
        if type(x) in [list, numpy.ndarray]:
            return type(x).__name__+'['+str(len(x))+']'
        return type(x).__name__

    def setName(self, name:str):
        if not re.match(r'^[a-zA-Z_][a-zA-Z_0-9]*$', name):
            raise ValueError('invalid name')
        self.__name = name

    def setValue(self, value):
        self.__value = value

    def setDescription(self, description):
        self.__description = description

    def eval(self, locals = {}):
        if type(self.__value) is str:
            try:
                # Evaluate expression (str)
                globals = vars(numpy)
                self.__evalValue = eval(self.__value, globals, locals)
            except Exception as e:
                # Error message if exception occurs
                self.__evalValue = 'error: '+str(e)
        else:
            # Pass value if not string
            self.__evalValue = self.__value
        # Add to locals
        locals[self.__name] = self.__evalValue

