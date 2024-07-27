from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from numpy import *
from xml.dom import minidom
import xml.etree.ElementTree as ET

from VariableItemModule import VariableItem

class VariableItemList(QtCore.QObject):

    # Signals
    valueChanged = Signal()

    def __init__(self, parent = None):
        super().__init__(parent)
        self.__list = []

    def list(self) -> list:
        return self.__list.copy()

    def at(self, index:int) -> VariableItem:
        return self.__list[index]

    def count(self) -> int:
        return len(self.__list)

    def names(self) -> list:
        return [item.name() for item in self.__list]

    def append(self, name:str, value, description:str = '') -> int:
        item = VariableItem(name, value, description, self)
        names = self.names()
        if name in names:
            index = names.index(name)
            self.__list[index] = item
            self.valueChanged.emit()
            return index
        else:
            self.__list.append(item)
            self.valueChanged.emit()
            return len(self.__list) - 1

    def swap(self, i1:int, i2:int) -> bool:
        if 0 <= i1 < len(self.__list) and 0 <= i2 < len(self.__list):
            self.__list[i1], self.__list[i2] = self.__list[i2], self.__list[i1]
            self.valueChanged.emit()
            return True
        else:
            return False

    def pop(self, index:int) -> VariableItem:
        item = self.__list.pop(index)
        self.valueChanged.emit()
        return item

    def eval(self, locals = {}):
        for item in self.__list:
            item.eval(locals)

    def __tostring(self, value):
        if type(value) in [list, ndarray]:
            texts = [self.__tostring(e) for e in value]
            return '[' + ','.join(texts) + ']'
        elif type(value) in [float, complex, float32, float64, complex64, complex128]:
            return '{:.14e}'.format(value)
        else:
            return str(value)
    
    def exportXml(self, path):
        root = ET.Element('root')
        for item in self.__list:
            e = ET.SubElement(root, 'variable')
            e.set('name', item.name())
            e_1 = ET.SubElement(e, 'description')
            e_1.text = item.description()
            e_2 = ET.SubElement(e, 'value')
            e_2.text = self.__tostring(item.value())
            e_3 = ET.SubElement(e, 'type')
            e_3.text = type(item.value()).__name__

        doc = minidom.parseString(ET.tostring(root, 'utf-8'))
        with open(path, 'w') as f:
            doc.writexml(f, encoding='utf-8', newl='\n', indent='', addindent='\t')

    def importXml(self, path):
        tree = ET.parse(path)
        root = tree.getroot()
        for element in root.findall('variable'):
            name = element.attrib['name']
            value = element.find('value').text
            description = element.find('description').text or ''
            typeName = element.find('type').text
            if typeName != 'str':
                try:
                    value = eval(value)
                except Exception:
                    pass
            # Add to list
            self.append(name, value, description)

