import logging

import numpy as np
import peakutils
from scipy.signal import savgol_filter

logging.basicConfig(filename='something.log',
					format='[%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)


def findpoints(raw, dataframe, buffer, poly, window, thresh, mindist, xstart, xend):
	basepoints = []
	frontpoints = []

	temp = raw
	# For each tissue
	# TODO: ABS FIXES IT BUT WTF
	# dataframe['disp'] = abs(dataframe['disp'])
	dataframe['disp'] = savgol_filter(temp, window, poly)
	peaks = peakutils.indexes(dataframe['disp'], thresh, mindist)
	if not (xstart == xend == 0):
		start_ind = (np.abs(dataframe['time'] - xstart)).argmin()
		end_ind = (np.abs(dataframe['time'] - xend)).argmin()
		peak_start = (np.abs(peaks - start_ind)).argmin()
		peak_end = (np.abs(peaks - end_ind)).argmin()
		peaks = peaks[peak_start:peak_end]

	peaks = peaks[2:-1]
	for peak in peaks:
		# For each point from peak towards the start
		for k in range(peak - buffer, 1, -1):
			dfdt = (dataframe['disp'][k] -
					dataframe['disp'][k - 1])
			# If the derivate hits zero, we have changed diection and set base.
			if dfdt <= 0:
				basepoints.append(k)
				break
		# For each point from peak towards the end
		for k in range(peak + buffer, len(dataframe['disp']) - 1, 1):
			dfdt = (dataframe['disp'][k + 1] - dataframe['disp'][k])
			# If the derivate hits zero, we have changed diection and set base.
			if dfdt >= 0:
				frontpoints.append(k)
				break
	# Call the findP function to find the points at 10%, 50%, 90%
	ten = findP(peaks, basepoints, frontpoints, dataframe['disp'], dataframe['time'], .10)
	fifty = findP(peaks, basepoints, frontpoints, dataframe['disp'], dataframe['time'], .50)
	eighty = findP(peaks, basepoints, frontpoints, dataframe['disp'], dataframe['time'], .20)
	ninety = findP(peaks, basepoints, frontpoints, dataframe['disp'], dataframe['time'], .90)

	return dataframe, peaks, basepoints, frontpoints, ten, fifty, eighty, ninety


def findP(peaks, bases, fronts, disp, time, perc):
	ypoints = []
	xpoints = []
	negypoints = []
	negxpoints = []

	# For each contraction
	for i in range(len(bases)):
		# Determines the baseline (explained in documentation)
		baseline = (disp[bases[i]] + disp[fronts[i]]) / 2
		# Set the y value that would be 10%, 50% or 90%
		ydiff = (disp[peaks[i]] - baseline) * perc
		yval = negyval = baseline + ydiff

		# For each point from basepoint towards peak
		for j in range(bases[i], peaks[i] + 1, 1):
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

		ypoints.append(yval)
		xpoints.append(xval)

		# For each point from peak towards frontpoint. Similar as above.
		for j in range(peaks[i], fronts[i] + 1, 1):
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
