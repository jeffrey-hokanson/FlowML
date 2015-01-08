from __future__ import division
from IPython.display import HTML, Javascript, display
import uuid

class HeatGrid:
	""" Provides a d3.js driven heatmap in the form of a grid.
	"""

	def __init__(self, X):
		""" Provide the numpy matrix that will be the center of the plot.
		"""
	
		# provide a unique identifier for this plot
		self.uuid = str(uuid.uuid4().hex)
		self.width = 500
		self.height = 500
	def show(self):
		# Generate HTML 
		h = """<!DOCTYPE html>
				<svg class="{}"> </svg>
			""".format(self.uuid)
		display(HTML(h))

		# Now run javascript
		s = """
			var chart = d3.select(".{self.uuid}")
						.attr("width", {self.width})
						.attr("height", {self.height})

			chart.append("rect")
				.attr("width", 100)
				.attr("height", 10)
				.style("fill", "red")
		""".format(self = self)
		#display(Javascript(s))
		print self.uuid


class CoordHeatGrid:
	""" Provides a d3.js driven heatmap in the form of a grid.
	"""

	def __init__(self, X):
		""" Provide the numpy matrix that will be the center of the plot.
		"""
	
		# provide a unique identifier for this plot
		self.uuid = str(uuid.uuid4().hex)
		self.width = 500
		self.height = 500
	def show(self):
		# Generate HTML 
		h = """<!DOCTYPE html>
				<table class="{}"> </table>
			""".format(self.uuid)

		# Now run javascript
		
		s = """ // Time to make the tables
		function tabulate(data, header) {
			var table = d3.select(".%s"),
				thead = table.append("thead"),
				tbody = table.append("tbody");

			thead.selectAll("tr")
				.data(header)
				.enter()
				.append("tr")
				.selectAll("th")
					.data(function(d) {return d;})
					.enter()
					.append("th")
					.attr("colspan", function(d) {return d.span;})
					.text(function(d) {return d.name;});

			// Create a row for each object in the data
			var rows = tbody.selectAll("tr")
				.data(data)
				.enter()
				.append("tr");

			// Create a cell in each row for each column
			var cells = rows.selectAll("td")
				.data(function(row) {
					return columns.map(function(column) {
						return {
							column: column,
							value: row[column]
						};
					});
				})
				.enter()
				.append("td")
				.html(function(d) {
					return d.value;
				});
			return table;
		}

		// Render the table
	
		var peopleTable = tabulate(data, [
			[{name: "Foo", span: 2}, {name: "Bar", span: 3}], 
			[{name: "1"}, {name: "2"}, {name: "3"}, {name: "4"}, {name: "5"}]
		]);		
		
		""" % (self.uuid, )
		display(HTML(h+"<script>"+s+"</script>"))

