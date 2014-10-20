from __future__ import division
import util
import itertools
import numpy as np
from ipython_progress import progress_bar
from copy import copy

# TODO: Multiprocessing using https://docs.python.org/2/library/multiprocessing.html


def sort_group(x, *args):
	"""Utility function sorting a set of lists by the first list
	"""
	I = sorted(range(len(x)), key = lambda k: x[k])		
	x = [x[i] for i in I]
	out = [x]
	for y in args:
		out.append( [y[i] for i in I])
	return out

class Threshold():
	def __init__(self, fd, thresholds, progress = False, method = 'recursive'):
		"""
		"""
		# Select only the keys that apply to this dataset
		threshold_keys = list(thresholds.keys())
		keys = []
		active_thresholds = {}
		for key in threshold_keys:
			try: 
				fd[key]
				keys.append(key)
				active_thresholds[key] = thresholds[key]
			except:
				pass
		self.keys = keys
		# number of rows
		self.n = fd[keys[0]].shape[0]
		
		if method == 'recursive':
			self.coords, self.counts = recursive_threshold(fd, active_thresholds, progress)
		elif method == 'product':
			self.coords, self.counts = product_threshold(fd, active_thresholds, progress)
		else:
			raise NotImplementedError

	def __eq__(self, other):
		"""Two threshold gates are equal if their counts and coordinates are equal"""
		
		c1, t1 = sort_group(self.coords, self.counts)
		c2, t2 = sort_group(other.coords, other.counts)
		n1 = self.n
		n2 = other.n

		if len(c1) != len(c2):
			return False
		
		if c1 != c2:
			return False

		# compute ratios of counts	
		r1 = [t/n1 for t in t1]
		r2 = [t/n2 for t in t2]
		# ensure the ratios match for each
		return  np.sum(np.abs(np.array(r1) - np.array(r2)))< 1e-10


	def __repr__(self):
		out = ''
		for coord, count in zip(self.coords, self.counts):
			for key in coord:
				out += '{}: {}, '.format(key, coord[key])
			out+=' -> {}\n'.format(count)
		return out


	def __getitem__(self, coord):
		""" Return the ratio of counts in the cooresponding coordinates, summing
			over unspecified coordinates."""
		try:
			active_keys = set(coord.keys())
		except:
			raise TypeError
		# Make sure we are not requesting an unallowed key
		for key in active_keys:
			if key not in self.keys:
				raise KeyError

		total = 0
		for c, n in zip(self.coords, self.counts):
			use = True
			for key in active_keys:
				if c[key] != coord[key]:
					use = False
					break
			if use:
				total += n
		return total/self.n

	def common_keys(*args, base_keys = None):
		""" Return minimial set of markers for provided threshold types.
		"""
		if base_keys is not None:
			s = set(base_keys)
		else:
			s = set(args[0].keys)
		# Iterate through provided Threshold members, choosing minimal set.
		for a in args[1:]:
			k = set(a.keys)
			s.intersection(k)
		return list(s)
			


def product_threshold(fd, thresholds, progress):
	keys = list(thresholds.keys())
	n = fd.shape[0]
	# number of distinct populations
	npop = 1
	# list of coordinates on each axis for itertools.product
	coords = []
	for key in keys:
		nsplits = len(thresholds[key])+1
		coords.append(range(0, nsplits))
		npop *= nsplits
	# precompute partitions
	splits = {}
	for j, key in enumerate(keys):
		key_splits = []
		cuts = thresholds[key] 
		for c in coords[j]:
			if c  == 0:
				val = (fd[key] < cuts[0])
			elif c == len(cuts):
				val = (fd[key]) > cuts[-1]
			elif c > 0:
				val = (fd[key] > cuts[c-1]) & (fd[key]< cuts[c])     
			key_splits.append(val)
		splits[key] = key_splits

	# Now compute all permutations
	product_iter = itertools.product(*coords)
		
	nonempty_coord = []
	nonempty_count = []
	for coord in product_iter:
		val = np.ones( (fd.shape[0],), dtype = bool)
		for c, key in zip(coord, keys):
			val *= splits[key][c]
		
		count = np.sum(val)
		if count > 0:
			tmp_coord = {}
			for c, key in zip(coord, keys):
				tmp_coord[key] = c
			nonempty_coord.append(tmp_coord)
			nonempty_count.append(count)

	return (nonempty_coord, nonempty_count)


def recursive_threshold(fd, thresholds, progress):
	keys = list(thresholds.keys())
	n = fd.shape[0]
	# number of distinct populations
	npop = 1
	# precompute partitions
	splits = {}
	for j, key in enumerate(keys):
		key_splits = []
		cuts = thresholds[key] 
		for c in range(len(cuts)+1):
			if c  == 0:
				val = (fd[key] < cuts[0])
			elif c == len(cuts):
				val = (fd[key]) > cuts[-1]
			elif c > 0:
				val = (fd[key] > cuts[c-1]) & (fd[key]< cuts[c])     
			key_splits.append(np.array(val))
		splits[key] = key_splits

	nonempty_coord = []
	nonempty_count = []
	
	# Recursive function
	def recurse(keys, val = None, coord = {}):
		if val == None:
			val = np.ones( (n,) , dtype = bool)
		new_keys = copy(keys)
		key = new_keys.pop(0)
		for k in range(len(thresholds[key])+1):
			# update coordinates
			new_coord = copy(coord)
			new_coord[key] = k
			# Apply 
			new_val = val*splits[key][k]
			count = np.sum(new_val)
			if count > 0:
				if len(new_keys) > 0:
					recurse(new_keys, new_val, new_coord)
				else:
					nonempty_coord.append(new_coord)
					nonempty_count.append(count)

	recurse(keys)
	return (nonempty_coord, nonempty_count) 
		






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
	
		
