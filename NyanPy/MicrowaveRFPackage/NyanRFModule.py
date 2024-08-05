import numpy as np
import os
import re

"""Loads SnP (touchstone) file
Args:
    path (str): SnP file path
Returns:
    s         (ndarray): S parameter vector
    frequency (ndarray): frequency vector
"""
def loadsnp(path:str) -> tuple:
    base, ext = os.path.splitext(path)
    matched = re.match(r'^.s[1-9][0-9]*p$', ext)
    if not matched:
        raise RuntimeError('loadsnp: invalid file extension')

    n = int(ext[2:-1])
    data = []
    with open(path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        line = line[:line.find('!')].strip().upper()
        if not line:
            continue
        if line[0] == '#': # Option line
            matched = re.match(r'#\s+(HZ|KHZ|MHZ|GHZ)\s+'\
                    +r'(S|Y|Z|G|H)\s+(MA|DB|RI)\s+R\s+[+-]?([0-9]*[.])?[0-9]+', line)
            if not matched:
                continue
            words = line.split()
            FREQ_UNITS = words[1]
            TYPE = words[2]
            FORMAT = words[3]
            Z0 = float(words[5])
        else:
            data += [float(s) for s in line.split()]

    if 'FREQ_UNITS' not in locals():
        raise RuntimeError('loadsnp: option line not found')

    columnCount = 2 * n**2 + 1
    rowCount = int(len(data) / columnCount)
    data = np.array(data).reshape((rowCount, columnCount))
    frequency = data[:, 0]
    frequency *= 1e3 if FREQ_UNITS == 'KHZ'\
            else 1e6 if FREQ_UNITS == 'MHZ'\
            else 1e9 if FREQ_UNITS == 'GHZ'\
            else 1
    reconst = lambda a, b, FORMAT: a * np.exp(1j * b * np.pi / 180.) if FORMAT == 'MA'\
            else 10**(a / 20.) * np.exp(1j * b * np.pi / 180.) if FORMAT == 'DB'\
            else a + 1j * b
    s = np.zeros((len(frequency), n, n), dtype=complex)
    indices = [(0, 0), (1, 0), (0, 1), (1, 1)] if n == 2\
            else [(i, j) for i in range(n) for j in range(n)]

    for k in range(len(frequency)):
        for m, (i, j) in enumerate(indices):
            a = data[k, 1 + 2 * m]
            b = data[k, 2 + 2 * m]
            s[k][i, j] = reconst(a, b, FORMAT)

    return (s, frequency)


"""Writes SnP (touchstone) file
Args:
    s          (ndarray): S parameter vector
    frequency  (ndarray): frequency vector
    path       (str)    : SnP file path
    FREQ_UNITS (str)    : 'HZ' (default), 'KHZ', 'MHZ' or 'GHZ'
    TYPE       (str)    : 'S'  (default), 'Y', 'Z', 'G' or 'H'
    FORMAT     (str)    : 'RI' (default), 'MA' or 'DB'
    Z0         (float)  : reference impedance, defaults to 50.0 (Ohm)
Returns:
    None
"""
def writesnp(s, frequency, path, FREQ_UNITS = 'HZ', TYPE = 'S', FORMAT = 'RI', Z0 = 50.):
    FREQ_UNITS = FREQ_UNITS.upper()
    TYPE = TYPE.upper()
    FORMAT = FORMAT.upper()
    n = np.size(s, 1)
    indices = [(0, 0), (1, 0), (0, 1), (1, 1)] if n == 2\
            else [(i, j) for i in range(n) for j in range(n)]

    # Option line
    text = '# '+FREQ_UNITS+' '+TYPE+' '+FORMAT+' R {:f}\n'.format(Z0)

    # Header line (comment)
    text += '{:<12}'.format('! FREQ('+FREQ_UNITS+')')
    for m, (i, j) in enumerate(indices):
        PREFIX = {'MA':('mag', 'ang'), 'DB':('db', 'ang'), 'RI':('re', 'im')}
        SUFFIX = ('{}{}' if n < 9 else '[{},{}]').format(i + 1, j + 1)
        text += '  {:<12}'.format(PREFIX[FORMAT][0]+TYPE+SUFFIX)
        text += '  {:<12}'.format(PREFIX[FORMAT][1]+TYPE+SUFFIX)
        if m == len(indices) - 1:
            text += '\n'
        elif (m + 1) % 4 == 0:
            text += '\n{:<12}'.format('!')

    # Data lines
    for k, freq_ in enumerate(frequency):
        UNIT = {'HZ':1e0, 'KHZ':1e3, 'MHZ':1e6, 'GHZ':1e9}
        text += '{:.6e}'.format(freq_ / UNIT[FREQ_UNITS])
        for m, (i, j) in enumerate(indices):
            x = s[k][i, j]
            a = np.abs(x) if FORMAT == 'MA'\
                    else 20 * np.log10(np.abs(x)) if FORMAT == 'DB'\
                    else np.real(x)
            b = np.angle(x) / np.pi * 180. if FORMAT in ['MA', 'DB']\
                    else np.imag(x)
            text += ' {:13.6e}'.format(a)
            text += ' {:13.6e}'.format(b)
            if m == len(indices) - 1:
                text += '\n'
            elif (m + 1) % 4 == 0:
                text += '\n{:<12}'.format('')

    # Write file
    with open(path, 'w') as f:
        f.write(text)


# S parameter --> T parameter
def stot(s):
    if s.ndim == 3:
        t = s.copy()
        for i in range(np.size(s, 0)):
            t[i] = stot(s[i])
        return t

    elif s.ndim == 2:
        if np.size(s, 0) != np.size(s, 1):
            raise RuntimeError('Not a square matrix!!!')

        if np.size(s, 0) != 2:
            raise RuntimeError('Must be a 2x2 matrix!!!')

        t = s.copy()
        dets = np.linalg.det(s)
        t[0, 0] =    -dets / s[1, 0]
        t[0, 1] =  s[0, 0] / s[1, 0]
        t[1, 0] = -s[1, 1] / s[1, 0]
        t[1, 1] =       1. / s[1, 0]
        return t

    else:
        raise RuntimeError('Unexpected dimension')


# T parameter --> S parameter
def ttos(t):
    if t.ndim == 3:
        s = t.copy()
        for i in range(np.size(t, 0)):
            s[i] = ttos(t[i])
        return s

    elif t.ndim == 2:
        if np.size(t, 0) != np.size(t, 1):
            raise RuntimeError('Not a square matrix!!!')

        if np.size(t, 0) != 2:
            raise RuntimeError('Must be a 2x2 matrix!!!')

        s = t.copy()
        dett = np.linalg.det(t)
        s[0, 0] =  t[0, 1] / t[1, 1]
        s[0, 1] =     dett / t[1, 1]
        s[1, 0] =       1. / t[1, 1]
        s[1, 1] = -t[1, 0] / t[1, 1]
        return s

    else:
        raise RuntimeError('Unexpected dimension')


# S parameter --> Z parameter
def stoz(s, zref = 50.):
    if s.ndim == 3:
        z = s.copy()
        for i in range(np.size(s, 0)):
            z[i] = stoz(s[i], zref)
        return z

    elif s.ndim == 2:
        if np.size(s, 0) != np.size(s, 1):
            raise RuntimeError('Not a square matrix!!!')

        # Port number
        n = np.size(s, 0)

        if type(zref) in [list, np.ndarray]:
            if len(zref) != n:
                raise RuntimeError('Zref vector length must be equal to the number of ports')
            else:
                zref = np.array(zref)
        else:
            zref_ = np.zeros(n, dtype=complex)
            zref_.fill(complex(zref))
            zref = zref_

        f = np.diag(0.5 / np.sqrt(np.abs(np.real(zref))))
        g = np.diag(zref)
        z = np.linalg.inv(f) @ np.linalg.inv(np.eye(n) - s) @ (s @ g + g.conj().T) @ f
        return z

    else:
        raise RuntimeError('Unexpected dimension')


# Z parameter --> S parameter
def ztos(z, zref = 50.):
    if z.ndim == 3:
        s = z.copy()
        for i in range(np.size(z, 0)):
            s[i] = ztos(z[i], zref)
        return s

    elif z.ndim == 2:
        if np.size(z, 0) != np.size(z, 1):
            raise RuntimeError('Not a square matrix!!!')

        # Port number
        n = np.size(s, 0)

        if type(zref) in [list, np.ndarray]:
            if len(zref) != n:
                raise RuntimeError('Zref vector length must be equal to the number of ports')
            else:
                zref = np.array(zref)
        else:
            zref_ = np.zeros(n, dtype=complex)
            zref_.fill(complex(zref))
            zref = zref_

        f = np.diag(0.5 / np.sqrt(np.abs(np.real(zref))))
        g = np.diag(zref)
        s = f @ (z - g.conj().T) @ np.linalg.inv(z + g) @ np.linalg.inv(f)
        return s

    else:
        raise RuntimeError('Unexpected dimension')


# Z parameter --> Y parameter
def ztoy(z):
    if z.ndim == 3:
        y = z.copy()
        for i in range(np.size(z, 0)):
            y[i] = ztoy(z[i])
        return y

    elif z.ndim == 2:
        if np.size(z, 0) != np.size(z, 1):
            raise RuntimeError('Not a square matrix!!!')

        y = np.linalg.inv(z)
        return y

    else:
        raise RuntimeError('Unexpected dimension')


# Z parameter --> H parameter
def ztoh(z):
    if z.ndim == 3:
        h = z.copy()
        for i in range(np.size(z, 0)):
            h[i] = ztoh(z[i])
        return h

    elif z.ndim == 2:
        if np.size(z, 0) != np.size(z, 1):
            raise RuntimeError('Not a square matrix!!!')

        if np.size(z, 0) != 2:
            raise RuntimeError('Must be a 2x2 matrix!!!')

        h = z.copy()
        detz = np.linalg.det(z)
        h[0, 0] =     detz / z[1, 1]
        h[0, 1] =  z[0, 1] / z[1, 1]
        h[1, 0] = -z[1, 0] / z[1, 1]
        h[1, 1] =       1. / z[1, 1]
        return h

    else:
        raise RuntimeError('Unexpected dimension')


# Z parameter --> ABCD parameter
def ztoa(z):
    if z.ndim == 3:
        a = z.copy()
        for i in range(np.size(z, 0)):
            a[i] = ztoa(z[i])
        return a

    elif z.ndim == 2:
        if np.size(z, 0) != np.size(z, 1):
            raise RuntimeError('Not a square matrix!!!')

        if np.size(z, 0) != 2:
            raise RuntimeError('Must be a 2x2 matrix!!!')

        a = z.copy()
        detz = np.linalg.det(z)
        a[0, 0] = z[0, 0] / z[1, 0]
        a[0, 1] =    detz / z[1, 0]
        a[1, 0] =      1. / z[1, 0]
        a[1, 1] = z[1, 1] / z[1, 0]
        return a

    else:
        raise RuntimeError('Unexpected dimension')


# Y parameter --> Z parameter
def ytoz(y):
    if y.ndim == 3:
        z = y.copy()
        for i in range(np.size(y, 0)):
            z[i] = ytoz(y[i])
        return z

    elif y.ndim == 2:
        if np.size(y, 0) != np.size(y, 1):
            raise RuntimeError('Not a square matrix!!!')

        if np.size(y, 0) != 2:
            raise RuntimeError('Must be a 2x2 matrix!!!')

        z = y.copy()
        dety = np.linalg.det(y)
        z[0, 0] =  y[1, 1] / dety
        z[0, 1] = -y[0, 1] / dety
        z[1, 0] = -y[1, 0] / dety
        z[1, 1] =  y[0, 0] / dety
        return z

    else:
        raise RuntimeError('Unexpected dimension')


# H parameter --> Z parameter
def htoz(h):
    if h.ndim == 3:
        z = h.copy()
        for i in range(np.size(h, 0)):
            z[i] = htoz(h[i])
        return z

    elif h.ndim == 2:
        if np.size(h, 0) != np.size(h, 1):
            raise RuntimeError('Not a square matrix!!!')

        if np.size(h, 0) != 2:
            raise RuntimeError('Must be a 2x2 matrix!!!')

        z = h.copy()
        deth = np.linalg.det(h)
        z[0, 0] =     deth / h[1, 1]
        z[0, 1] =  h[0, 1] / h[1, 1]
        z[1, 0] = -h[1, 0] / h[1, 1]
        z[1, 1] =       1. / h[1, 1]
        return z

    else:
        raise RuntimeError('Unexpected dimension')


# ABCD parameter --> Z parameter
def atoz(a):
    if a.ndim == 3:
        z = a.copy()
        for i in range(np.size(a, 0)):
            z[i] = atoz(a[i])
        return z

    elif a.ndim == 2:
        if np.size(a, 0) != np.size(a, 1):
            raise RuntimeError('Not a square matrix!!!')

        if np.size(a, 0) != 2:
            raise RuntimeError('Must be a 2x2 matrix!!!')

        z = a.copy()
        deta = np.linalg.det(a)
        z[0, 0] = a[0, 0] / a[1, 0]
        z[0, 1] =    deta / a[1, 0]
        z[1, 0] =      1. / a[1, 0]
        z[1, 1] = a[1, 1] / a[1, 0]
        return z

    else:
        raise RuntimeError('Unexpected dimension')


# Maximum available gain (MAG, GMAX)
def maxgain(s):
    if s.ndim == 3:
        maxgain_vector = np.zeros(np.size(s, 0))
        for i in range(np.size(s, 0)):
            maxgain_vector[i] = maxgain(s[i])
        return maxgain_vector

    elif s.ndim == 2:
        if np.size(s, 0) != np.size(s, 1):
            raise RuntimeError('Not a square matrix!!!')

        if np.size(s, 0) != 2:
            raise RuntimeError('Must be a 2x2 matrix!!!')

        k = stabilityfactor(s)
        s12 = np.abs(s[0, 1])
        s21 = np.abs(s[1, 0])
        if k > 1.:
            # Maximum available gain
            return (k - np.sqrt(k**2 - 1)) * (s21 / s12)
        else:
            # Maximum stable gain
            return (s21 / s12)

    else:
        raise RuntimeError('Unexpected dimension')


# Stability factor (K factor)
def stabilityfactor(s):
    if s.ndim == 3:
        k = np.zeros(np.size(s, 0))
        for i in range(np.size(s, 0)):
            k[i] = stabilityfactor(s[i])
        return k

    elif s.ndim == 2:
        if np.size(s, 0) != np.size(s, 1):
            raise RuntimeError('Not a square matrix!!!')

        if np.size(s, 0) != 2:
            raise RuntimeError('Must be a 2x2 matrix!!!')

        det = np.abs(np.linalg.det(s))
        s11 = np.abs(s[0, 0])
        s12 = np.abs(s[0, 1])
        s21 = np.abs(s[1, 0])
        s22 = np.abs(s[1, 1])
        k = (1. - s11**2 - s22**2 + det**2) / (2. * s21 * s12)
        return k

    else:
        raise RuntimeError('Unexpected dimension')


# Group delay
def groupdelay(s, frequency):
    if np.size(s, 0) != len(frequency):
        raise RuntimeError('S and frequency must be the same vector length')

    if s.ndim == 3:
        if np.size(s, 0) == 1:
            raise RuntimeError('Group delay calculation requires two or more data points')
        else:
            tg = s.copy()
            dphi = np.mod(np.angle(s[1]) - np.angle(s[0]), 2 * np.pi)
            domega = 2 * np.pi * (frequency[1] - frequency[0])
            tg[0] = dphi / domega

            for i in range(1, np.size(s, 0)):
                dphi = np.mod(np.angle(s[i]) - np.angle(s[i - 1]), 2 * np.pi)
                domega = 2 * np.pi * (frequency[i] - frequency[i - 1])
                tg[i] = dphi / domega
            return tg
    else:
        raise RuntimeError('Unexpected dimension')





if __name__ == '__main__':
    s, frequency = loadsnp('sample.s2p')
    s = ztos(atoz(ztoa(htoz(ztoh(ytoz(ztoy(stoz(ttos(stot(s))))))))))
    writesnp(s, frequency, 'out.s2p', 'HZ', 'S', 'RI')

