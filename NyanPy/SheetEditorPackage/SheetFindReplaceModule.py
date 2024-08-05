from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys
import os

class SheetFindReplace(QtWidgets.QDialog):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.__findTextLineEdit = QtWidgets.QLineEdit('^[a-zA-Z]+$')
        self.__replaceTextLineEdit = QtWidgets.QLineEdit()
        self.__replaceCheckBox = QtWidgets.QCheckBox('Replace:')
        self.__allScopeRadioButton = QtWidgets.QRadioButton('All')
        self.__selectedScopeRadioButton = QtWidgets.QRadioButton('Selected')
        self.__buttonGroup = QtWidgets.QButtonGroup()
        self.__buttonGroup.addButton(self.__allScopeRadioButton)
        self.__buttonGroup.addButton(self.__selectedScopeRadioButton)

        self.setupUi()
        self.setWindowTitle('Find & Replace')

    def find(self) -> str:
        return self.__findTextLineEdit.text()

    def replace(self) -> tuple:
        checked = self.__replaceCheckBox.isChecked()
        text = self.__replaceTextLineEdit.text()
        return (checked, text)

    def scope(self) -> str:
        button = self.__buttonGroup.checkedButton()
        return button.text() if button else ''

    def setupUi(self):
        self.__replaceCheckBox.setChecked(False)
        self.__replaceTextLineEdit.setEnabled(False)
        self.__replaceCheckBox.clicked[bool].connect(self.__replaceTextLineEdit.setEnabled)
        self.__allScopeRadioButton.setChecked(True)
        self.__selectedScopeRadioButton.setChecked(False)
        buttonbox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok\
                | QtWidgets.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.accept)
        buttonbox.rejected.connect(self.reject)
        cheatsheet = QtWidgets.QLabel()
        cheatsheet.setAlignment(Qt.AlignTop)
        cheatsheet.setStyleSheet('border: 1px solid #404040;')
        cheatsheet.setText('Regular Expressions:\n*\t0 or more\n+\t1 or more\n'\
                '?\t0 or 1\n.\tAny character\n(a|b)\ta or b\n[abc]\tRange (a or b or c)\n'\
                '[^abc]\tNot (a or b or c)\n[a-q]\tLower case letter from a to q\n'\
                '[A-Q]\tUpper case letter from A to Q\n[0-7]\tDigit from 0 to 7\n'\
                '\\s\tWhitespace\n\\d\tDigit\n\\w\tWord\n')
        # Layouts
        vboxlayout = QtWidgets.QVBoxLayout()
        vboxlayout.addWidget(QtWidgets.QLabel('Find what:'))
        vboxlayout.addWidget(self.__findTextLineEdit)
        vboxlayout.addWidget(self.__replaceCheckBox)
        vboxlayout.addWidget(self.__replaceTextLineEdit)
        vboxlayout.addWidget(QtWidgets.QLabel('Search scope:'))
        vboxlayout.addWidget(self.__allScopeRadioButton)
        vboxlayout.addWidget(self.__selectedScopeRadioButton)
        vboxlayout.addStretch()
        vboxlayout.addWidget(buttonbox)
        hboxlayout = QtWidgets.QHBoxLayout(self)
        hboxlayout.addLayout(vboxlayout)
        hboxlayout.addWidget(cheatsheet)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = FindReplace()
    ex.show()
    sys.exit(app.exec())

