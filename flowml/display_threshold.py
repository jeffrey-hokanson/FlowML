from __future__ import division
from threshold import *
from IPython.display import HTML, Javascript,  display
from IPython.core.display import display_html
import uuid
import json

def threshold_sparkline(coords, X, column_names = None, show_percentages = True):
	"""
	See discusion on http://www.edwardtufte.com/bboard/q-and-a-fetch-msg?msg_id=0001OR
	"""

	# Element IDs cannot start with numbers
	id_ = 'X'+str(uuid.uuid4().hex)
	if column_names is not None:
		assert len(column_names) == X.shape[1]
	if column_names is None:
		show_percentages = False

	nrows = len(coords)
	ncol = len(coords[0])

	html = """<!DOCTYPE html>
	<meta charset="utf-8">
	<style>
	.chart rect {
	  fill: steelblue;
	}

	.chart text {
	  fill: white;
	  font: 10px sans-serif;
	  text-anchor: end;
	}
	
	.threshold table, th, td {
		font: 10px Arial;
	}

		path {
				stroke: steelblue;
				stroke-width: 1;
				fill: none;
			}
			
			.axis {
			  shape-rendering: crispEdges;
			}

			.x.axis line {
			  stroke: lightgrey;
			}

			.x.axis .minor {
			  stroke-opacity: .5;
			}

			.x.axis path {
			  display: none;
			}

			.y.axis line, .y.axis path {
			  fill: none;
			  stroke: #000;
			}
	</style>
	"""
	# See: http://bl.ocks.org/benjchristensen/2579599
	
	# Setup header
	table = """<table class = "threshold", id = "%s">
			<tr>
			""".format(id_)
	coord = coords[0]
	# Establish key order
	keys = [key for key in coord]
	# Column for each coordinate
	for key in keys:
		table += "<th>{}</th>".format(key)
	# Add a column for the sparkline
	table+="<th></th>"
	# Columns showing actual percentages
	if show_percentages:
		for name in column_names:
			table+="<th>{}</th>".format(name)
	table+="</tr>"

	
	# Build rows

	for j, (coord, X_row) in enumerate(zip(coords, X)):
		table += "<tr>"
		# label coordinates
		for key in keys:
			table += "<td>"
			if False:
				table += key + " "
			
			if coord[key] == 0:
				table += "-"
			else:
				table += "+"*coord[key]
			table += "</td>"

		# Insert graphic
		table += '<td> <svg class = "sparkline", id = "{}"></svg></td>'.format(id_ + "Z%d" % (j,) )

		# Insert percentages
		if show_percentages:
			for x in X_row:
				table += '<td> %5.3g%%</td>' % (100.*x,)

	table+="</table>"

	# Write the table	
	h = HTML(html+table)
	display(h)	


	# Function to 
	# http://www.tnoda.com/blog/2013-12-19
	data_str = json.dumps(list(X[0]))	
	js="""
		function sparkline(elemId, data){
			var width = 100;
			var height = 25;
			
			var x = d3.scale.linear().domain([0, data.length]).range([0, width]);
			var y = d3.scale.linear().domain(d3.extent(data)).range([height, 0]);
			
			var line = d3.svg.line()
					.x(function(d, i) { return x(i);})
					.y(function(d, i) { return y(d);});
			var plot = d3.select(elemId)
				.attr('width', width)
				.attr('height', height);

			plot.append("path");	
			plot.append("svg:path").attr("d", line(data));
		}
		""" 
		
	for j, X_row in enumerate(X):
		js += "var data = "+json.dumps(list(X_row)) + ";\n"
		js += "sparkline(%s, data);" % (id_+'Z%d' %(j,),) +"\n"
	
	display(Javascript(js))

