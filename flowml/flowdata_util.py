from flowdata import FlowData
import pandas as pd


def concat(fdarray):
	"""Merge FlowData together
	"""

	
	pd_data = [fd.panda for fd in fdarray]
	new_panda = pd.concat(pd_data)
	md = fdarray[0]._metadata
	# Clean up the metadata
	md['$FIL'] = 'merged data'
	newfd = FlowData(panda = new_panda, metadata = md)

	return newfd
	
	
			 
