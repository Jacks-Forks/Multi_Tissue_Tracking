import peakutils
from scipy.signal import savgol_filter


def findpoints(dataframe, buffer, poly, window, thresh, mindist):
    origin = dataframe

    peaks = []
    basepoints = []
    frontpoints = []
    ten = []
    fifty = []
    ninety = []

    for i in range(len(dataframe)):
        dataframe[i]['disp'] = savgol_filter(origin[i]['disp'], window,
                                             poly)
        dataframe[i]['disp'] = dataframe[i]['disp'] * -1
        peaks.append(
            peakutils.indexes(dataframe[i]['disp'], thresh, mindist))
        peaks[i] = peaks[i][1:-1]
        basepoints.append([])
        frontpoints.append([])
        ten.append([])
        fifty.append([])
        ninety.append([])
        for peak in peaks[i]:
            for k in range(peak - buffer, 1, -1):
                dfdt = (dataframe[i]['disp'][k] -
                        dataframe[i]['disp'][k - 1])
                if dfdt <= 0:
                    basepoints[i].append(k)
                    break
            for k in range(peak + buffer, len(dataframe[i]['disp']), 1):
                dfdt = (dataframe[i]['disp'][k + 1] - dataframe[i]['disp'][k])
                if dfdt >= 0:
                    frontpoints[i].append(k)
                    break

        ten[i] = findP(peaks[i], basepoints[i], frontpoints[i], dataframe[i]
                       ['disp'], dataframe[i]['time'], .10)
        fifty[i] = findP(peaks[i], basepoints[i], frontpoints[i], dataframe[i]
                         ['disp'], dataframe[i]['time'], .50)
        ninety[i] = findP(peaks[i], basepoints[i], frontpoints[i], dataframe[i]
                          ['disp'], dataframe[i]['time'], .90)
    return dataframe, peaks, basepoints, frontpoints, ten, fifty, ninety


def findP(peaks, bases, fronts, disp, time, perc):
    ypoints = []
    xpoints = []
    negypoints = []
    negxpoints = []

    for i in range(len(bases)):
        ydiff = (disp[peaks[i]] - disp[bases[i]]) * perc
        yval = disp[bases[i]] + ydiff

        for j in range(bases[i], peaks[i], 1):
            if disp[j] > yval:
                slope = (disp[j] - disp[j - 1]) / (time[j] - time[j - 1])
                xval = ((yval - disp[j - 1]) / slope) + time[j - 1]
                break
        ypoints.append(yval)
        xpoints.append(xval)

        negydiff = (disp[peaks[i]] - disp[fronts[i]]) * perc
        negyval = disp[fronts[i]] + negydiff
        for j in range(peaks[i], fronts[i], 1):
            if disp[j] < negyval:
                slope = (disp[j] - disp[j - 1]) / (time[j] - time[j - 1])
                negxval = ((negyval - disp[j - 1]) / slope) + time[j - 1]
                break

        negypoints.append(negyval)
        negxpoints.append(negxval)
    return xpoints, ypoints, negxpoints, negypoints
