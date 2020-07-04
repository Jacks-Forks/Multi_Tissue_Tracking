import peakutils
from scipy.signal import savgol_filter


def findpoints(dataframe, buffer, poly, window, thresh, mindist):
    # Store a copy of original
    # TODO: Is this actually storing an original? Or is it rewritten every time
    origin = dataframe


    peaks = []
    basepoints = []
    frontpoints = []
    ten = []
    fifty = []
    ninety = []

    # For each tissue
    for i in range(len(dataframe)):
        # Apply the sav-gol filter with specified parameters
        dataframe[i]['disp'] = savgol_filter(origin[i]['disp'], window,
                                             poly)
        # Flip the data, Because when distance is smallest is actually the peak of the contraction
        dataframe[i]['disp'] = dataframe[i]['disp'] * -1
        # Use pythons peakutils to find the peaks with specified parameters
        peaks.append(
            peakutils.indexes(dataframe[i]['disp'], thresh, mindist))
        # Delete the first and last peak ( Avoids possible errors with half peaks)
        peaks[i] = peaks[i][1:-1]
        basepoints.append([])
        frontpoints.append([])
        ten.append([])
        fifty.append([])
        ninety.append([])
        # For each peak
        for peak in peaks[i]:
            # For each point from peak towards the start
            for k in range(peak - buffer, 1, -1):
                dfdt = (dataframe[i]['disp'][k] -
                        dataframe[i]['disp'][k - 1])
                # If the derivate hits zero, we have changed diection and set base.
                if dfdt <= 0:
                    basepoints[i].append(k)
                    break
            # For each point from peak towards the end
            for k in range(peak + buffer, len(dataframe[i]['disp']), 1):
                dfdt = (dataframe[i]['disp'][k + 1] - dataframe[i]['disp'][k])
                # If the derivate hits zero, we have changed diection and set base.
                if dfdt >= 0:
                    frontpoints[i].append(k)
                    break
        # Call the findP function to find the points at 10%, 50%, 90%
        # TODO: Naming
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

    # For each contraction
    for i in range(len(bases)):
        # Determines the baseline (explained in documentation)
        # TODO: Add to documentation
        baseline = (disp[bases[i]] + disp[fronts[i]]) / 2
        # Set the y value that would be 10%, 50% or 90%
        ydiff = (disp[peaks[i]] - baseline) * perc
        yval = negyval = baseline + ydiff

        # For each point from basepoint towards peak
        for j in range(bases[i], peaks[i], 1):
            # If yval is less the the basepoint it will not be on graph
            if yval < disp[bases[i]]:
                # Set the val to the basepoint as thats the closest possible value
                # Only really happens with 10% and rarely (ie, very arrhythmic contractions)
                xval = time[bases[i]]
                yval = disp[bases[i]]
                break
            # If the displacemnt goes above the vyal
            elif disp[j] > yval:
                # Find the slope btween the point before and after the expected value and do a linear fit
                # TODO: Add docs
                slope = (disp[j] - disp[j - 1]) / (time[j] - time[j - 1])
                xval = ((yval - disp[j - 1]) / slope) + time[j - 1]
                break
            # If disp is exactly yval no need for linear fit
            elif disp[j] == yval:
                xval = time[j]
                break
            # TODO: Add if yval > disp[peaks]??

        ypoints.append(yval)
        xpoints.append(xval)

        # For each point from peak towards frontpoint. Similar as above.
        for j in range(peaks[i], fronts[i], 1):
            if negyval < disp[fronts[i]]:
                negxval = time[fronts[i]]
                negyval = disp[fronts[i]]
                break
            elif disp[j] < negyval:
                slope = (disp[j] - disp[j - 1]) / (time[j] - time[j - 1])
                negxval = ((negyval - disp[j - 1]) / slope) + time[j - 1]
                break
            elif (j == fronts[i] - 1):
                slope = (disp[j + 1] - disp[j]) / \
                    (time[j + 1] - time[j])
                negxval = ((negyval - disp[j]) / slope) + time[j]
                break
            elif disp[j] == negyval:
                negxval = time[j]
                break

        negypoints.append(negyval)
        negxpoints.append(negxval)
    return xpoints, ypoints, negxpoints, negypoints
