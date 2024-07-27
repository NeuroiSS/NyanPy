from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import re

class SyntaxHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.__rules = []
        self.__multiLineRules = []

    def addRule(self, expr, fmt):
        self.__rules.append((expr, fmt))

    def addRules(self, exprs, fmt):
        for expr in exprs:
            self.__rules.append((expr, fmt))

    def addMultiLineRule(self, start, stop, fmt):
        self.__multiLineRules.append((start, stop, fmt))

    def highlightKeywords(self, text):
        for (expr, fmt) in self.__rules:
            for match in re.finditer(expr, text):
                start, end = match.span()
                if self.format(start) != QtGui.QTextCharFormat():
                    continue
                self.setFormat(start, end - start, fmt)

    def highlightMultiLine(self, text):
        blockState = self.previousBlockState()
        startIndex = 0
        index = 0
        while index < len(text):
            if blockState == -1:
                matched = False
                for i in range(len(self.__multiLineRules)):
                    start, stop, fmt = self.__multiLineRules[i]
                    # Regex
                    for match in re.finditer(start, text):
                        if index == match.start():
                            startIndex = index
                            index += match.end() - match.start()
                            matched = True
                            break
                    if matched:
                        blockState = i
                        break
                if not matched:
                    index += 1
            else:
                start, stop, fmt = self.__multiLineRules[blockState]
                match = re.match(stop, text[index:])
                if match:
                    index += match.end()
                    length = index - startIndex
                    self.setFormat(startIndex, length, fmt)
                    blockState = -1
                else:
                    index += 1

        if blockState != -1:
            start, stop, fmt = self.__multiLineRules[blockState]
            length = len(text) - startIndex
            self.setFormat(startIndex, length, fmt)

        self.setCurrentBlockState(blockState)

    @override
    def highlightBlock(self, text):
        # Highlight Multi-line Comments
        self.highlightMultiLine(text)

        # Highlight Keywords
        self.highlightKeywords(text)

        # Whitespaces
        fmt = QtGui.QTextCharFormat()
        fmt.setForeground(QtGui.QColor('#262626'))
        for match in re.finditer(r'\s', text):
            start, end = match.span()
            self.setFormat(start, end - start, fmt)


class SyntaxHighlighter_Python(SyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)

        # Strings
        fmt = QtGui.QTextCharFormat()
        fmt.setForeground(QtGui.QColor('#99ad6a'))
        self.addMultiLineRule("'''", "'''", fmt)
        self.addMultiLineRule('"""', '"""', fmt)
        self.addMultiLineRule("'", "'", fmt)
        self.addMultiLineRule('"', '"', fmt)

        # Comments
        fmt = QtGui.QTextCharFormat()
        fmt.setForeground(QtGui.QColor('#888888'))
        fmt.setFontItalic(True)
        self.addRule(r'#.*$', fmt)

        # Spectial Methods: e.g. __name__
        fmt = QtGui.QTextCharFormat()
        fmt.setForeground(QtGui.QColor('#fad07a'))
        self.addRule(r'\b__\w+__\b', fmt)

        # Decorators: e.g. @staticmethod
        self.addRule(r'@\w+', fmt)

        # Class Definitions: class <class name>
        self.addRule(r'(?<=class\s)\w+', fmt)

        # Function Definitions: def <function name>
        self.addRule(r'(?<=def\s)\w+', fmt)

        # Built-in Constants
        self.addRules([r'\bFalse\b', r'\bTrue\b', r'\bNone\b', r'\bNotImplemented\b', r'\bEllipsis\b'], fmt)

        # Built-in Functions
        keywords  = [r'\babs\b', r'\baiter\b', r'\ball\b', r'\banext\b', r'\bany\b', r'\bascii\b']
        keywords += [r'\bbin\b', r'\bbool\b', r'\bbreakpoint\b', r'\bbytearray\b', r'\bbytes\b']
        keywords += [r'\bcallable\b', r'\bchr\b', r'\bclassmethod\b', r'\bcompile\b', r'\bcomplex\b']
        keywords += [r'\bdelattr\b', r'\bdict\b', r'\bdir\b', r'\bdivmod\b']
        keywords += [r'\benumerate\b', r'\beval\b', r'\bexec\b']
        keywords += [r'\bfilter\b', r'\bfloat\b', r'\bformat\b', r'\bfrozenset\b']
        keywords += [r'\bgetattr\b', r'\bglobals\b']
        keywords += [r'\bhasattr\b', r'\bhash\b', r'\bhelp\b', r'\bhex\b']
        keywords += [r'\bid\b', r'\binput\b', r'\bint\b', r'\bisinstance\b', r'\bissubclass\b', r'\biter\b']
        keywords += [r'\blen\b', r'\blist\b', r'\blocals\b']
        keywords += [r'\bmap\b', r'\bmax\b', r'\bmemoryview\b', r'\bmin\b']
        keywords += [r'\bnext\b']
        keywords += [r'\bobject\b', r'\boct\b', r'\bopen\b', r'\bord\b']
        keywords += [r'\bpow\b', r'\bprint\b', r'\bproperty\b']
        keywords += [r'\brange\b', r'\brepr\b', r'\breversed\b', r'\bround\b']
        keywords += [r'\bset\b', r'\bsetattr\b', r'\bslice\b', r'\bsorted\b', r'\bstaticmethod\b', r'\bstr\b', r'\bsum\b', r'\bsuper\b']
        keywords += [r'\btuple\b', r'\btype\b']
        keywords += [r'\bvars\b']
        keywords += [r'\bzip\b']
        self.addRules(keywords, fmt)

        # Numbers
        fmt = QtGui.QTextCharFormat()
        fmt.setForeground(QtGui.QColor('#cf6a4c'))
        self.addRule(r'\b(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?\b', fmt)
        self.addRule(r'\b0[xX][0-9a-fA-F]+\b', fmt)
        self.addRule(r'\b0[oO][0-7]+\b', fmt)
        self.addRule(r'\b0[bB][0-1]+\b', fmt)

        # Keywords
        fmt = QtGui.QTextCharFormat()
        fmt.setForeground(QtGui.QColor('#8197bf'))
        keywords  = [r'\band\b', r'\bas\b', r'\bassert\b', r'\basync\b', r'\bawait\b']
        keywords += [r'\bbreak\b']
        keywords += [r'\bclass\b', r'\bcontinue\b']
        keywords += [r'\bdef\b', r'\bdel\b']
        keywords += [r'\belif\b', r'\belse\b', r'\bexcept\b']
        keywords += [r'\bfinally\b', r'\bfor\b', r'\bfrom\b']
        keywords += [r'\bglobal\b']
        keywords += [r'\bif\b', r'\bimport\b', r'\bin\b', r'\bis\b']
        keywords += [r'\blambda\b']
        keywords += [r'\bnonlocal\b', r'\bnot\b']
        keywords += [r'\bor\b']
        keywords += [r'\bpass\b']
        keywords += [r'\braise\b', r'\breturn\b']
        keywords += [r'\btry\b']
        keywords += [r'\bwhile\b', r'\bwith\b']
        keywords += [r'\byield\b']
        self.addRules(keywords, fmt)


class SyntaxHighlighter_Matlab_GNUOctave(SyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)

        # Strings
        fmt = QtGui.QTextCharFormat()
        fmt.setForeground(QtGui.QColor('#99ad6a'))
        fmt.setFontItalic(True)
        self.addMultiLineRule(r"(?<=[^\)\]\}a-zA-Z_0-9])'", r"'", fmt)
        self.addMultiLineRule(r'"', r'"', fmt)

        # Comments
        fmt = QtGui.QTextCharFormat()
        fmt.setForeground(QtGui.QColor('#888888'))
        self.addRule(r'%.*$', fmt)
        self.addMultiLineRule('%{', '%}', fmt)

        # Numbers
        fmt = QtGui.QTextCharFormat()
        fmt.setForeground(QtGui.QColor('#cf6a4c'))
        self.addRule(r'\b(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?\b', fmt)
        self.addRule(r'\b0[xX][0-9a-fA-F]+\b', fmt)
        self.addRule(r'\b0[oO][0-7]+\b', fmt)
        self.addRule(r'\b0[bB][0-1]+\b', fmt)

        # Keywords
        fmt = QtGui.QTextCharFormat()
        fmt.setForeground(QtGui.QColor('#8197bf'))
        keywords  = [r'\b__FILE__\b', r'\b__LINE__\b']
        keywords += [r'\bbreak\b']
        keywords += [r'\bcase\b', r'\bcatch\b', r'\bclassdef\b', r'\bcontinue\b']
        keywords += [r'\bdo\b']
        keywords += [r'\belse\b', r'\belseif\b', r'\bend\b', r'\bend_try_catch\b', r'\bend_unwind_protect\b']
        keywords += [r'\bendclassdef\b', r'\bendenumeration\b', r'\bendevents\b', r'\bendfor\b', r'\bendfunction\b']
        keywords += [r'\bendif\b', r'\bendmethods\b', r'\bendparfor\b', r'\bendproperties\b', r'\bendswitch\b']
        keywords += [r'\bendwhile\b', r'\benumeration\b', r'\bevents\b']
        keywords += [r'\bfor\b', r'\bfunction\b']
        keywords += [r'\bglobal\b']
        keywords += [r'\bif\b']
        keywords += [r'\bmethods\b']
        keywords += [r'\botherwise\b']
        keywords += [r'\bparfor\b', r'\bpersistent\b', r'\bproperties\b']
        keywords += [r'\breturn\b']
        keywords += [r'\bswitch\b']
        keywords += [r'\btry\b']
        keywords += [r'\buntil\b', r'\bunwind_protect\b', r'\bunwind_protect_cleanup\b']
        keywords += [r'\bwhile\b']
        self.addRules(keywords, fmt)

        # Built-in Functions
        fmt = QtGui.QTextCharFormat()
        fmt.setForeground(QtGui.QColor('#fad07a'))
        keywords  = [r'\berror\b', r'\bwarning\b', r'\bsize\b', r'\bclear\b', r'\breshape\b']
        keywords += [r'\beye\b', r'\bones\b', r'\bzeros\b', r'\blinspace\b', r'\blogspace\b', r'\brand\b']
        keywords += [r'\bexp\b', r'\blog\b', r'\blog10\b', r'\bsqrt\b']
        keywords += [r'\babs\b', r'\barg\b', r'\bconj\b', r'\bimag\b', r'\breal\b']
        keywords += [r'\bsin\b', r'\bcos\b', r'\btan\b', r'\basin\b', r'\bacos\b', r'\batan\b', r'\batan2\b']
        keywords += [r'\bsinh\b', r'\bcosh\b', r'\btanh\b', r'\basinh\b', r'\bacosh\b', r'\batanh\b']
        keywords += [r'\bsum\b', r'\bprod\b', r'\bceil\b', r'\bfloor\b', r'\bround\b']
        keywords += [r'\bmax\b', r'\bmin\b', r'\bsign\b', r'\bmean\b', r'\bstd\b', r'\bcov\b']
        self.addRules(keywords, fmt)

