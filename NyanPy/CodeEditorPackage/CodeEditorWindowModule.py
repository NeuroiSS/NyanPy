from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys
import os

from CodeEditorModule import CodeEditor

class CodeEditorWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        codeEditor = CodeEditor()
        self.setCentralWidget(codeEditor)
        self.setWindowTitle(codeEditor.windowTitle())
        codeEditor.windowTitleChanged.connect(self.setWindowTitle)

        actions = {a.text():a for a in codeEditor.actions()}
        menuBar = self.menuBar()

        # File menu
        menu = menuBar.addMenu('File')
        menu.addAction(codeEditor.action('Open...'))
        menu.addAction(codeEditor.action('Save'))
        menu.addAction(codeEditor.action('Save as...'))

        # Tab styles
        menu = menuBar.addMenu('Tab style')
        menu.addAction(codeEditor.action('Hard tab'))
        menu.addAction(codeEditor.action('Soft tab'))

        # Languages
        menu = menuBar.addMenu('Language')
        menu.addAction(codeEditor.action('Text'))
        menu.addAction(codeEditor.action('Python'))
        menu.addAction(codeEditor.action('Matlab/GNU Octave'))

