
import numpy as np
# Constants

# EHT
# All units SI
# Meters
#postLen = .012
#tissueHeight = .0115
#radius = .0005
#Pascals (N/m^2)
#youngs = 1330000


'''
Force Parameters
'''


def force(youngs, radius, l_r, a_r, l_l, a_l, deltaT):
    forceRatio = ((a_r**2) * ((3 * l_r) - a_r)) / \
        ((a_l**2) * ((3 * l_l) - a_l))
    youngs = int(youngs)
    Lcoef_t = (3 * np.pi * youngs * (radius**4))
    Lcoef_b = (2 * (a_l**2) * ((3 * l_l) - a_l))
    Lcoef = Lcoef_t / Lcoef_b
    Lforce = []

    for i in range(len(deltaT)):
        deltaL = deltaT[i] / (1 + forceRatio)
        Lforce.append(Lcoef * deltaL)

    std = np.std(Lforce)
    avg = sum(Lforce) / len(Lforce)
    return avg, std


'''
Time Parameters
'''


def beating_freq(time, peaks):
    timediff = []
    for i in range(len(peaks) - 1):
        timediff.append(1 / (time[peaks[i + 1]] - time[peaks[i]]))
    std = np.std(timediff)
    avg = sum(timediff) / len(timediff)
    return avg, std


def time2pk(tens, peaks, time):
    t2pke = []
    for i in range(len(peaks)):
        t2pke.append(time[peaks[i]] - tens[0][i])
    std = np.std(t2pke)
    avg = sum(t2pke) / len(t2pke)
    return avg, std


def time2rel50(fifty, peaks, time):
    t2rel = []
    for i in range(len(fifty[2])):
        t2rel.append(fifty[2][i] - time[peaks[i]])
    std = np.std(t2rel)
    avg = sum(t2rel) / len(t2rel)
    return avg, std


def time2rel90(ninety, peaks, time):
    t2rel = []
    for i in range(len(ninety[2])):
        t2rel.append(ninety[2][i] - time[peaks[i]])
    std = np.std(t2rel)
    avg = sum(t2rel) / len(t2rel)
    return avg, std


def t50(fifty, time):
    t50 = []
    for i in range(len(fifty[0])):
        t50.append(fifty[2][i] - fifty[0][i])
    std = np.std(t50)
    avg = sum(t50) / len(t50)
    return avg, std


def c50(peaks, fifty, time):
    c50 = []
    for i in range(len(fifty[0])):
        c50.append(time[peaks[i]] - fifty[0][i])
    std = np.std(c50)
    avg = sum(c50) / len(c50)
    return avg, std


def r50(peaks, fifty, time):
    r50 = []
    for i in range(len(fifty[2])):
        r50.append(fifty[2][i] - time[peaks[i]])
    std = np.std(r50)
    avg = sum(r50) / len(r50)
    return avg, std


'''
Slope Parameters
'''


def dfdt(ninety, ten, time):
    dft = []
    for i in range(len(ten[0])):
        slope = (ninety[1][i] - ten[1][i]) / (ninety[0][i] - ten[0][i])
        dft.append(slope)
    std = np.std(dft)
    avg = sum(dft) / len(dft)
    return avg, std


def negdfdt(ninety, ten, time):
    negdft = []
    for i in range(len(ten[2])):
        slope = (ten[3][i] - ninety[3][i]) / (ten[2][i] - ninety[2][i])
        negdft.append(slope)
    std = np.std(negdft)
    avg = sum(negdft) / len(negdft)
    return avg, std
