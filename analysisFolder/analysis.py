import peakutils
from scipy.signal import savgol_filter


def findpoints(dataframe, buffer, poly, window, thresh, mindist):
    origin = dataframe

    peaks = []
    basepoints = []
    frontpoints = []

    for i in range(len(dataframe)):
        dataframe[i]['disp'] = savgol_filter(origin[i]['disp'], window,
                                             poly)
        dataframe[i]['disp'] = dataframe[i]['disp'] * -1
        peaks.append(
            peakutils.indexes(dataframe[i]['disp'], thresh, mindist))
        peaks[i] = peaks[i][1:-1]
        basepoints.append([])
        frontpoints.append([])
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

    return dataframe, peaks, basepoints, frontpoints
