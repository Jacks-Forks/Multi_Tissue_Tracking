import glob
import importlib

import app
import models
import numpy as np
import pandas as pd




# Constants

# EHT
# All units SI
# Meters
# postLen = .012
# tissueHeight = .0115
# radius = .0005
# Pascals (N/m^2)
# youngs = 1330000


def carry_calcs(all_data, files):
	beat_freq = []
	time2pks = []
	time50rel = []
	time80rel = []
	time90rel = []
	t_50 = []
	c_50 = []
	r_50 = []
	slope = []
	negslope = []
	freqCOV = []

	devforce = []
	actforce = []
	pasforce = []
	path = files[0].split('csvfiles')[0]
	for i, file in enumerate(files):
		time = all_data[i][0]['time']
		disp = all_data[i][0]['disp']
		bases = all_data[i][2]
		fronts = all_data[i][3]
		peaks = all_data[i][1]
		ten = all_data[i][4]
		fifty = all_data[i][5]
		eighty = all_data[i][6]
		ninety = all_data[i][7]
		peakdist = []
		basedist = []
		devdist = []

		for j in range(len(peaks)):
			# Find the distances for sys, dias, and dev force
			# TODO: CHECK SIgn of 7
			peakdist.append(7 + disp[peaks[j]])
			basedist.append(7 + ((disp[bases[j]] + disp[fronts[j]])/2))
			devdist.append(peakdist[j] - basedist[j])
		tissue_object = models.get_tissue_by_csv(file)
		bio_object = tissue_object.video.bio_reactor

		if bio_object.bio_reactor_number != 0:
			loc = tissue_object.post
			l_r = bio_object.posts[loc].right_post_height
			l_l = bio_object.posts[loc].left_post_height
			a_r = bio_object.posts[loc].right_tissue_height
			a_l = bio_object.posts[loc].left_tissue_height
			radius = .227
		else:
			# If other system, set these as heights
			l_r = 12
			l_l = 12
			a_r = 11.5
			a_l = 11.5
			radius = .5
		# TODO: Better Define youngs + radius, be editable. FIND UNITS FOR FORCE
		youngs = 13300.00
		actforce.append(force(youngs, radius, l_r, a_r, l_l, a_l, peakdist))
		pasforce.append(force(youngs, radius, l_r, a_r, l_l, a_l, basedist))
		devforce.append(force(youngs, radius, l_r, a_r, l_l, a_l, devdist))
		beat_freq.append(beating_freq(time, peaks))
		time2pks.append(time2pk(ten, peaks, time))
		time50rel.append(time2rel50(fifty, peaks, time))
		time80rel.append(time2rel80(eighty, peaks, time))
		time90rel.append(time2rel90(ten, peaks, time))
		t_50.append(t50(fifty))
		c_50.append(c50(peaks, fifty, time))
		r_50.append(r50(peaks, fifty, time))
		slope.append(dfdt(ninety, ten))
		negslope.append(negdfdt(ninety, ten))
		freqCOV.append(beat_freq[i][1] / beat_freq[i][0])
	output(actforce, devforce, pasforce, beat_freq, freqCOV, time2pks, time50rel, time80rel, time90rel, t_50, c_50, r_50, slope,
		   negslope, path, files)
	return


def reload_database():
	app.app.app_context().push()

	importlib.reload(models)
	return


def output(actforce, devforce, pasforce, beat_freq, freqCOV, time2pks, time50rel, time80rel, time90rel, t_50, c_50, r_50, slope,
		   negslope, path, files):
	summaryfile = open(path + 'summary.csv', 'w')
	summaryfile.write('Tissue' + ',' +
					  'Active Force' + ',' +
					  'Active Force STD' + ',' +
					  'Passive Force' + ',' +
					  'Passive Force STD' + ',' +
					  'Developed Force' + ',' +
					  'Developed Force STD' + ',' +
					  'Average Beat Rate' + ',' +
					  'Average Beat Rate STD' + ',' +
					  'Beat Rate COV' + ',' +
					  'T2PK' + ',' +
					  'T2PK STD' + ',' +
					  'T50' + ',' +
					  'T50 STD' + ',' +
					  'C50' + ',' +
					  'C50 STD' + ',' +
					  'R50' + ',' +
					  'R50 STD' + ',' +
					  'T2Rel50' + ',' +
					  'T2Rel50 STD' + ',' +
					  'T2Rel80' + ',' +
					  'T2Rel80 STD' + ',' +
					  'T2Rel90' + ',' +
					  'T2Rel90 STD' + ',' +
					  'dfdt' + ',' +
					  'dfdt STD' + ',' +
					  'negdfdt' + ',' +
					  'negdfdt STD' + ',' +
					  '\n'
					  )
	for i in range(len(t_50)):
		tissue_object = models.get_tissue_by_csv(files[i])
		summaryfile.write(f'{tissue_object.tissue_number}' + ',' +
						  str(actforce[i][0]) + ',' +
						  str(actforce[i][1]) + ',' +
						  str(pasforce[i][0]) + ',' +
						  str(pasforce[i][1]) + ',' +
						  str(devforce[i][0]) + ',' +
						  str(devforce[i][1]) + ',' +
						  str(beat_freq[i][0]) + ',' +
						  str(beat_freq[i][1]) + ',' +
						  str(freqCOV[i]) + ',' +
						  str(time2pks[i][0]) + ',' +
						  str(time2pks[i][1]) + ',' +
						  str(t_50[i][0]) + ',' +
						  str(t_50[i][1]) + ',' +
						  str(c_50[i][0]) + ',' +
						  str(c_50[i][1]) + ',' +
						  str(r_50[i][0]) + ',' +
						  str(r_50[i][1]) + ',' +
						  str(time50rel[i][0]) + ',' +
						  str(time50rel[i][1]) + ',' +
						  str(time80rel[i][0]) + ',' +
						  str(time80rel[i][1]) + ',' +
						  str(time90rel[i][0]) + ',' +
						  str(time90rel[i][1]) + ',' +
						  str(slope[i][0]) + ',' +
						  str(slope[i][1]) + ',' +
						  str(negslope[i][0]) + ',' +
						  str(negslope[i][1]) + ',' +
						  '\n'
						  )

	summaryfile.close()
	return


'''
Force Parameters
'''


# TODO: Add explanations for each. Also go through and verify

def force(youngs, radius, l_r, a_r, l_l, a_l, deltaT):
	forceRatio = ((a_r ** 2) * ((3 * l_r) - a_r)) / \
				 ((a_l ** 2) * ((3 * l_l) - a_l))
	youngs = int(youngs)
	Lcoef_t = (3 * np.pi * youngs * (radius ** 4))
	Lcoef_b = (2 * (a_l ** 2) * ((3 * l_l) - a_l))
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

def time2rel80(eighty, peaks, time):
	t2rel = []
	for i in range(len(eighty[2])):
		t2rel.append(eighty[2][i] - time[peaks[i]])
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


def t50(fifty):
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


def dfdt(ninety, ten):
	dft = []
	for i in range(len(ten[0])):
		slope = (ninety[1][i] - ten[1][i]) / (ninety[0][i] - ten[0][i])
		dft.append(slope)
	std = np.std(dft)
	avg = sum(dft) / len(dft)
	return avg, std


def negdfdt(ninety, ten):
	negdft = []
	for i in range(len(ten[2])):
		slope = (ten[3][i] - ninety[3][i]) / (ten[2][i] - ninety[2][i])
		negdft.append(slope)
	std = np.std(negdft)
	avg = sum(negdft) / len(negdft)
	return avg, std
