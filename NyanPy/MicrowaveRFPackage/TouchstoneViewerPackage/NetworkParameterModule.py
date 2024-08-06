from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
from enum import StrEnum
import sys
import os
import numpy as np

sys.path.append(os.pardir)
import NyanRFModule as nyanRF


class ParamTypes(StrEnum):
    S_PARAMETER = 'S Parameter'
    Z_PARAMETER = 'Z Parameter'
    Y_PARAMETER = 'Y Parameter'
    H_PARAMETER = 'H Parameter'
    ABCD_PARAMETER = 'ABCD Parameter'
    GROUP_DELAY = 'Group Delay'
    STABILITY_FACTOR = 'Stability Factor'
    MAX_GAIN = 'Maximum Gain'


class NetworkParameter(QtCore.QObject):
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self.__freq = np.array([])
        self.__data = {}
        self.__text = ''

    def freq(self):
        return self.__freq

    def text(self) -> str:
        return self.__text

    def vector(self, param:ParamTypes, n:int, m:int) -> np.ndarray:
        if param not in self.__data:
            return None

        A = self.__data[param]
        if A.ndim == 1:
            return A
        elif A.ndim == 3:
            if n < np.size(A, 1) and m < np.size(A, 2):
                return np.array([a[n][m] for a in A])

        return None

    def load(self, path:str):
        S, freq = nyanRF.loadsnp(path)
        self.__freq = freq
        self.__text = os.path.basename(path)
        if np.size(S) == 0:
            raise RuntimeError('No data was loaded')

        self.__data[ParamTypes.S_PARAMETER] = S
        self.__data[ParamTypes.Z_PARAMETER] = nyanRF.stoz(S)
        self.__data[ParamTypes.Y_PARAMETER] = nyanRF.ztoy(nyanRF.stoz(S))
        self.__data[ParamTypes.GROUP_DELAY] = nyanRF.groupdelay(S, freq)

        numPorts = np.size(S[0], 0)
        if numPorts == 2:
            # 2-Port network parameters
            self.__data[ParamTypes.H_PARAMETER] = nyanRF.ztoh(nyanRF.stoz(S))
            self.__data[ParamTypes.ABCD_PARAMETER] = nyanRF.ztoa(nyanRF.stoz(S))
            self.__data[ParamTypes.STABILITY_FACTOR] = nyanRF.stabilityfactor(S)
            self.__data[ParamTypes.MAX_GAIN] = nyanRF.maxgain(S)

