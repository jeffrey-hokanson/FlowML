from __future__ import division
from threshold import *

from IPython.display import HTML, Javascript,  display
from IPython.core.display import display_html
import uuid
import json



class threshold_table:

	def __init__(self, thresholds, names, title = None, plot_type = 'sparkline'):
		"""Provide a list of coordinates to display and optional associated percentages
		"""

		self.id_ = 'X'+str(uuid.uuid4().hex)
		self.thresholds = [thresholds]
		self.names = [names]
		self.plot_type = [plot_type]

	def add_thresholds(self, thresholds, names, title = None):
		"""Add additional types of data (i.e., enter 
		"""
		pass

	def show(self):
		""" Render the table
		"""
		pass
