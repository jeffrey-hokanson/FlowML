from __future__ import division
import numpy as np
import flowml as fml
import pandas as pd

def random_flowdata(ncol = 5, nrow = 100, keys = None):
	if keys is None:
		keys = ['CD{}'.format(j+1) for j in range(ncol)]
	else:
		ncol = len(keys)
	data = np.random.lognormal(mean = 1., sigma = 1., size = (nrow, ncol))
	df = pd.DataFrame(data, columns = keys)
	fd = fml.FlowData(panda = df)
	return fd


def test_keys():
	"""Provide a key not in the dataset, ensure we don't fail
	"""
	keys = ['CD1','CD2','CD3']
	fd = random_flowdata(keys = keys)
	# Baseline
	thresholds = {'CD1' : [5]} 
	t1 = fml.Threshold(fd, thresholds, method = 'product')
	# Key not in the dataset
	thresholds['X'] = [10]
	t2 = fml.Threshold(fd, thresholds, method = 'product')

	assert t1.keys == t2.keys
	# Assert that the counts in the thresholds are equal
	assert t1 == t2	


def test_recursive():
	fd = random_flowdata(ncol = 12, nrow = int(1e5))
	thresholds = {}
	for key in fd.columns:
		thresholds[key] = [10.]
	t1 = fml.Threshold(fd, thresholds)
	t2 = fml.Threshold(fd, thresholds, method = 'product')
	assert t1 == t2


def test_getitem():
	"""Check that we assign the ratios when looking at only one key.
	"""
	n = int(1e5)
	fd = random_flowdata(ncol = 12, nrow = n)
	thresholds = {}
	for key in fd.columns:
		thresholds[key] = [10.]
	t = fml.Threshold(fd, thresholds)

	for key in fd.columns:
		count = np.sum(fd[key] < thresholds[key])
		assert count/n == t[{key: 0}]
		count = np.sum(fd[key] > thresholds[key])
		assert count/n == t[{key: 1}]

def test_intersection():
	fd1 = random_flowdata(ncol = 2, nrow = 100)
	fd2 = random_flowdata(ncol = 3, nrow = 100)
	thresholds = {}
	for key in fd2.columns:
		thresholds[key] = [10.]
	t1 = fml.Threshold(fd1, thresholds)
	t2 = fml.Threshold(fd2, thresholds)

	common_keys = t1.common_keys(t2)
	assert sorted(common_keys) == sorted(['CD1', 'CD2'])
	
