from __future__ import division
import os

from threshold import *

from IPython.display import HTML, Javascript,  display
from IPython.core.display import display_html
import uuid
import json
from copy import copy
import numpy as np

ALLOWED_PLOT_TYPES = ['sparkline', 'ratio']

class threshold_table:

	def __init__(self, thresholds, names, title = None, plot_type = 'sparkline'):
		"""Provide a list of coordinates to display and optional associated percentages
		"""

		self.id_ = 'X'+str(uuid.uuid4().hex)
		self.thresholds = [thresholds]
		self.names = [names]
		self.titles = [title]

		assert plot_type in ALLOWED_PLOT_TYPES
		self.plot_types = [plot_type]
		
		assert len(thresholds) == len(names)

		# TODO: Add getter/setter
		self.display_headers_every_n_rows = 5


	def add_thresholds(self, thresholds, names, title = None, plot_type = 'sparkline'):
		"""Add additional types of data (i.e., enter 
		"""
		self.thresholds += [thresholds]
		self.names += [names]
		self.titles.append(title)
		self.plot_types.append(plot_type)
		self.coords = None
		self.Xs = None

	def compute(self):
		""" Perform expensive computation
		"""
		
		# Stack the thresholds for computation and then separate back out
		tstack = [t for tt in self.thresholds for t in tt]
		coords, Xstack = threshold_expression_matrix(tstack)
		
		# Unroll into separate X for each coordinate
		Xs = []
		j = 0
		for t in self.thresholds:
			Xs.append(copy(Xstack[:,j:(j+len(t))]))
			j += len(t)

		self.coords = coords
		self.Xs = Xs

	
	def show(self, filename = None, limit = 100):
		""" Render the table
		"""

		if self.coords is None or self.Xs is None:
			self.compute()

		coords = copy(self.coords)
		Xs = copy(self.Xs)

		# Ensure we aren't asking for more populations than we have
		limit = min(limit, len(coords))

		# TODO: enable user sorting
		I = np.argsort(-np.sum(Xs[0],axis =1))
		coords = [coords[i] for i in I[0:limit]]
		Xs = [np.array([X[i] for i in I[0:limit]]) for X in Xs]
		


		# Establish order for keys
		keys = [key for key in coords[0]]

		def make_header():
			t = "<tr>"
			for key in keys:
				t += '<td class = "threshold_head">{}</td>'.format(key)

			for names, plot_type in zip(self.names, self.plot_types):
				# empty for plot if specified
				if plot_type is not None:
					if plot_type is 'sparkline':
						plot_name = ''
					if plot_type is 'ratio':
						plot_name = 'ratio'
					t += '<td class = "threshold_head">%s</td>' %(plot_name,)
				for name in names:
					t += '<td class = "threshold_head">{}</td>'.format(name)

			t += '</tr>'
			return t 

		# Render table
		table = """<table class = "threshold", id = "%s">""".format(self.id_)
		# Header
		table += '<thead><tr>'
		table += '<th colspan="%d" scope = "col">Coordinates</th>' % (len(keys),)
		
		for title, names in zip(self.titles, self.names):
			table += '<th colspan="%d" scope = "col">' % (len(names)+1,)
			table += title
			table += '</th>'
		table += '</thead>'
		table += '<tbody>'	
		# Table body
		for row, coord in enumerate(coords):
			# Add header
			if row % self.display_headers_every_n_rows == 0:
				table += make_header()
			# Start a normal row
			table += '<tr>'
	
			for key in keys:
				table += '<td class="threshold_coord">'
				if coord[key] == 0:
					table += '-'
				else:
					table += '+'*coord[key]
				table += '</td>'

		
			for k, X in enumerate(Xs):
				# Insert graphic
				table += '<td> <svg class = "sparkline", id = "{}"></svg></td>'.format(self.id_ + "Z%d_%d" % (k,row) )
				for x in X[row]:
					table += '<td> %5.3g%%</td>' % (100.*x,)

			table += '</tr>'
		table += '</tbody>'
		table += '</table>'



		# Load javascript
		js_name = os.path.join(os.path.dirname(__file__), 'sparkline.js')
		with open(js_name) as f:
			js = f.read()

		js_name = os.path.join(os.path.dirname(__file__), 'ratio_color.js')
		# Add javascript for plotting
		with open(js_name) as f:
			js += f.read()

		for row, coord in enumerate(coords):
			for k, (X, plot_type) in enumerate(zip(Xs, self.plot_types)):
				X_row = X[row]
				elemid = self.id_+'Z%d_%d' %(k,row)
				if plot_type is 'sparkline':
					js += "var data = "+json.dumps(list(X_row)) + ";\n"
					js += "sparkline(%s, data);" % (elemid,) +"\n"
				if plot_type is 'ratio':
					js += "ratio_color(%s,1,0,10);" % (elemid,) +'\n'	



		# Load the css formating options
		css_name = os.path.join(os.path.dirname(__file__), 'threshold_sparkline.css')
		with open(css_name) as f:
			css = f.read()

		html = "<!DOCTYPE html><html>"
		html += '<style>'+css+'</style>'
		html += '<body>' + table + '</body>'
		if filename is not None:
			html += '<script src="http://d3js.org/d3.v3.min.js" charset="utf-8"></script>'
		html += '<script>' + js + '</script>'
		html +="</html>"

		if filename is not None:
			with open(filename, 'w') as f:
				f.write(html)
				f.close()
			return None
		else:
			return HTML(html) 






