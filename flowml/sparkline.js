function sparkline(elemId, data){
	var width = 100;
	var height = 25;
	var margin = 2;
	var x = d3.scale.linear().domain([0, data.length - 1]).range([0+margin, width-margin]);
	var y = d3.scale.linear().domain(d3.extent(data)).range([height-margin, 0+margin]);
	
	var line = d3.svg.line()
			.x(function(d, i) { return x(i);})
			.y(function(d, i) { return y(d);});
	var plot = d3.select(elemId)
		.attr('width', width)
		.attr('height', height);

	plot.append("path");	
	plot.append("svg:path").attr("d", line(data));
}
