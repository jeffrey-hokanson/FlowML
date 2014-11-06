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

	def __init__(self, *args, **kwargs):
		"""Provide a list of coordinates to display and optional associated percentages.
		Note, for calling arguments, see the add_thresholds function.
		"""

		
		self.id_ = 'X'+str(uuid.uuid4().hex)
		self.thresholds = []
		self.names = []
		self.titles = []
		self.plot_types = []
		self.scalings = []
		self.short_titles = []
		# TODO: Add getter/setter
		self.display_headers_every_n_rows = 5

		self.expression_plots = []
		self.expression_plot_types = []
		self.expression_plot_titles = []
		self.add_thresholds(*args, **kwargs)

	def add_thresholds(self, thresholds, names, title = None, plot_type = 'sparkline', scaling = None, short_title = None):
		"""Add additional types of data (i.e., enter 
		"""
		
		assert len(thresholds) == len(names)
		assert plot_type in ALLOWED_PLOT_TYPES
		if short_title is None:
			short_title = title


		self.thresholds += [thresholds]
		self.names += [names]
		self.titles.append(title)
		self.plot_types.append(plot_type)
		self.scalings.append(scaling)
		self.short_titles.append(short_title)


		# Reset the coordinates if we've added a new set
		self.coords = None
		self.Xs = None


	def add_expression(self, channel, title = None, plot_type = 'sparkline'):
		""" Add a plot showing the expression of marker in this category
		"""
		self.expression_plots.append(channel)
		self.expression_plot_types.append(plot_type)
		if title is None:
			title = channel + ' Expression'
		self.expression_plot_titles.append(title)

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

	
	def show(self, rows = None, filename = None, limit = None):
		""" Render the table
			rows = 
		"""

		if self.coords is None or self.Xs is None:
			self.compute()

		coords = copy(self.coords)
		Xs = copy(self.Xs)

		# Ensure we aren't asking for more populations than we have
		if limit is None:
			limit = 100
			limit = min(limit, len(coords))
		if rows is None:
			rows = slice(0,limit)

		# TODO: enable user sorting
		I = np.argsort(-np.sum(Xs[0],axis =1))
		coords = [coords[i] for i in I[rows]]
		Xs = [np.array([X[i] for i in I[rows]]) for X in Xs]
	
		# Compute bulk properties for selected expression channels
		bulk_q1 = {}
		bulk_q3 = {}
		bulk_median = {}
		for channel in self.expression_plots:
			bulk_q1[channel] = [ [np.percentile(t.fd[channel], 25) for t in tt] for tt in self.thresholds]
			bulk_q3[channel] = [ [np.percentile(t.fd[channel], 75) for t in tt] for tt in self.thresholds]
			bulk_median[channel] = [ [np.median(t.fd[channel]) for t in tt] for tt in self.thresholds]



		# Establish order for keys
		keys = [key for key in coords[0]]

		def make_header():
			t = "<tr>"
			for key in keys:
				t += '<td class = "threshold_head">{}</td>'.format(key)

			for names, plot_type in zip(self.names, self.plot_types):
				# empty for plot if specified
				if 'sparkline' in plot_type:
					t += '<td class = "threshold_head"></td>' 
				if 'ratio' in plot_type:
					t += '<td class = "threshold_head">ratio</td>' 
				
				for name in names:
					t += '<td class = "threshold_head">{}</td>'.format(name)
			
			# Expression profiles
			for name in self.names:
				for title in self.expression_plot_titles:
					t += '<td class = "threshold_head">{}</td>'.format(title)

			t += '</tr>'
			return t 

		# Render table
		table = """<table class = "threshold", id = "%s">""".format(self.id_)
		# Header
		table += '<thead><tr>'
		# Coordinates
		table += '<th colspan="%d" scope = "col">Coordinates</th>' % (len(keys),)
		# Percenatages table 
		for title, names, plot_type in zip(self.titles, self.names, self.plot_types):
			# number of plots for this set of thresholds
			nplots = 0
			if 'ratio' in plot_type:
				nplots += 1
			if 'sparkline' in plot_type:
				nplots +=1 
			table += '<th colspan="%d" scope = "col">' % (len(names)+nplots,)
			table += title
			table += '</th>'	
		# Expression plots
		if len(self.expression_plots) > 0:
			for title in self.short_titles:
				table += '<th colspan="%d" scope = "col">' % (len(self.expression_plots), )
				table += title
				table += '</th>'

		table += '</thead>'
		table += '<tbody>'


		# Load javascript
		js_filenames = ['sparkline.js', 'ratio_color.js', 'expression.js']
		js = ''
		for name in js_filenames:
			js_name = os.path.join(os.path.dirname(__file__), name)
			with open(js_name) as f:
				js += f.read()

		# Table body
		for row, coord in enumerate(coords):
			# Add header
			if row % self.display_headers_every_n_rows == 0:
				table += make_header()
			# Start a normal row
			table += '<tr>'
	
			# Coordinates
			for key in keys:
				table += '<td class="threshold_coord">'
				if coord[key] == 0:
					table += '-'
				else:
					table += '+'*coord[key]
				table += '</td>'

			# Percentages of Cells
			for k, (X, scaling) in enumerate(zip(Xs, self.scalings)):
				
				# Scale if requested
				if scaling is None:
					row_vals = X[row]
				else:
					row_vals = scaling*X[row]

				# Insert graphics 
				
				plot_type = self.plot_types[k]
				if 'sparkline' in plot_type:
					elem_id = self.id_+'Z%d_%d_sparkline' %(k,row)
					table += '<td> <svg class = "sparkline", id = "{}"></svg></td>'.format(elem_id )
					js += "var data = "+json.dumps(list(row_vals)) + ";\n"
					js += "sparkline(%s, data);" % (elem_id,) +"\n"

				if 'ratio' in plot_type: 
					elem_id = self.id_+'Z%d_%d_ratio' %(k,row)
					table += '<td> <svg class = "sparkline", id = "{}"></svg></td>'.format(elem_id)
					ratio = row_vals[-1]/row_vals[0]
					#if row_vals[0] == 0 and row_vals[-1] == 0:
					#	ratio = 0.
					#if row_vals[0] == 0:
					#	ratio = float('inf')
					ratio_string = json.dumps(ratio)
					js += "ratio_color(%s,%s);" % (elem_id, ratio_string) +'\n'	

				# Insert row values into table
				if scaling is None:
					for x in row_vals:
						table += '<td> %5.3g%%</td>' % (100.*x,)
				else:
					for x in row_vals:
						table += '<td> %5.1f</td>' % (x,)
	
			# Expression Profiles
			if len(self.expression_plots) > 0:
				for j, threshold in enumerate(self.thresholds):
					cells_in_threshold = []
					for t in threshold:
						cells_in_threshold.append(t.in_coord(coord))
					#print self.expression_plots
					for k, channel in enumerate(self.expression_plots):
						elem_id = self.id_+'Z%d_expression_%d_%d' %(row, j, k)
						table += '<td> <svg class = "sparkline", id = "{}"></svg></td>'.format(elem_id)
						
						# Reformat data to be used by javascript
						coordinate = {}
						coordinate['median'] = [np.median(fd[channel]) for fd in cells_in_threshold]
						coordinate['q3'] = [np.percentile(fd[channel], 75) for fd in cells_in_threshold]
						coordinate['q1'] = [np.percentile(fd[channel], 25) for fd in cells_in_threshold]
						background = {}
						background['median'] = bulk_median[channel][j]
						background['q1'] = bulk_q1[channel][j]
						background['q3'] = bulk_q3[channel][j]
						js += "var coordinate = "+json.dumps(coordinate) + ";\n"
						js += "var background = "+json.dumps(background) + ";\n"
						js += "expression(%s, coordinate, background);" % (elem_id,) +"\n"
							
					#for t in threshold:
						



			table += '</tr>'
		table += '</tbody>'
		table += '</table>'





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






