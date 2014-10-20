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
