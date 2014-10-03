from __future__ import division
import util
import itertools
import numpy as np
from ipython_progress import progress_bar

# TODO: Multiprocessing using https://docs.python.org/2/library/multiprocessing.html

def threshold_gate(fdarray, thresholds, relative_to = None, unapplied = True, progress = True):
	"""

	unapplied - Include a setting where a threshold gate is not applied on a channel.
		e.g., if gating on CD45 and CD34, include a combination where only CD34 is gated on
	"""


	# Standardize input
	fdarray = util.make_list(fdarray)

    # Build a list of coordinates to iterate over based on the provided
    # thresholds.
	coords = []
	keys = list(thresholds.keys())
	# Number of populations that will be considered
	npop = 1
	for key in keys:
		nsplits = len(thresholds[key])+1
		if unapplied is True:
			coords.append(range(-1,nsplits))
			npop *= nsplits+1
		else:
			coords.append(range(0,nsplits))
			npop *= nsplits
    # Pre-compute action of thresholds (saves about 40%)
	all_coord_splits = []
	for fd in fdarray:	
		coord_splits = []
		for key, coord in zip(keys,coords):
			splits = []
			for c in coord:
				cuts = thresholds[key]
				if c  == 0:
					val = (fd[key] < cuts[0])
				elif c == len(cuts):
					val = (fd[key]) > cuts[-1]
				elif c > 0:
					val = (fd[key] > cuts[c-1]) & (fd[key]< cuts[c])     
				if c >=0:
					splits.append(val)
			splits = np.vstack(splits)
			coord_splits.append(splits)
		all_coord_splits.append(coord_splits)


	# Similarly precompute the baseline number
	if relative_to is None:
		baselines = [ fd.shape[0] for fd in fdarray]
	else:
		baselines = [ np.sum(fd[relative_to]) for fd in fdarray]

	# Iterate over every permutation
	row_names = []
	rows = []
	scores = []

	product_iter = itertools.product(*coords)
	if progress:
		product_iter = progress_bar(product_iter, expected_size = npop, update_every = 500)
	for coord in product_iter:
		string_tmp = ''

		# Construct the name of the current set
		for key, c in zip(keys, coord):
			cuts = thresholds[key]
			if len(cuts) == 1:
				if c == 0:
					string_tmp += '/{}- '.format(key)
				elif c == 1:
					string_tmp += '/{}+ '.format(key)

			elif len(cuts) == 2:
				if c == 0:
					string_tmp += '/{}- '.format(key)
				elif c == 1:
					string_tmp += '/{} lo'.format(key)
				elif c == 2:
					string_tmp += '/{} hi'.format(key)
		
		# Now build the counts for each set
		row = np.zeros((len(fdarray),) )
		for j, (baseline, fd, coord_splits) in enumerate(zip(baselines, fdarray, all_coord_splits)):
			val = np.ones( (fd.shape[0],), dtype = bool)
			for c, splits in zip(coord, coord_splits):
				if c >= 0:
					val *= splits[c]

			count = np.sum(val)
			row[j] = count/baseline

		# Now see if the row we have gathered is interesting
		# Every non-empty/ non-constant row will be included	
		score = ((np.max(row) - np.min(row))/np.max(row))*np.mean(row)
		
		if score > 0:
			row_names.append(string_tmp)
			rows.append(row)
			scores.append(score)

	# Rank rows
	scores = np.array(scores)
	I = np.argsort(-scores)
	
	rows = np.vstack(rows).T
	rows = rows[:,I]
	row_names = [row_names[j] for j in I] 
	return rows, row_names
	
		
