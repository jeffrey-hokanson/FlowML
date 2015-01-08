function expression(elemId, coordinate, background){
	var width = 100;
	var height = 25;
	var margin = 2;
	var x = d3.scale.linear().domain([0, coordinate["median"].length - 1]).range([0+margin, width-margin]);

	var all_data = coordinate["median"]
		.concat(background["median"])
		.concat(coordinate["q1"])
		.concat(coordinate["q3"])
		.concat(background["q1"])
		.concat(background["q3"]);

	var y = d3.scale.linear().domain(d3.extent(all_data)).range([height-margin, 0+margin]);


	console.log("Expression");	


	var plot = d3.select(elemId)
		.attr('width', width)
		.attr('height', height);

	plot.append("path");	
	
	// https://stackoverflow.com/questions/13263153/whats-the-absolute-shortest-d3-area-example	
	/*
	coord_range = []
	for (var i = 0; i < coordinate["median"].length; i++){
		coord_range.push([y(coordinate["q1"][i]), y(coordinate["q3"][i]) ]);
	}
	*/
	
	// reformat range data
	
	var coord_data = [];
	var background_data = []
	for (var i = 0; i < coordinate["median"].length; i++){
		if (!isNaN(coordinate["q1"][i])){
			coord_data.push({ ind:i, 
							q1:coordinate["q1"][i],
							q2:coordinate["median"][i],
							q3:coordinate["q3"][i],
						});
		}
		if (!isNaN(background["q1"][i])){
			background_data.push({ 
							ind:i,
							q1:background["q1"][i],
							q2:background["median"][i],
							q3:background["q3"][i]
						});
		}
	}
	console.log(coord_data);
	var area = d3.svg.area()
		.x(function (d) { return x(d["ind"]); })
		.y0(function (d) { return y(d["q1"]);})
		.y1(function (d) { return y(d["q3"]);});

	var median = d3.svg.line()
			.x(function(d, i) { return x(d["ind"]);})
			.y(function(d, i) { return y(d["q2"]);});

	// Plot background data
	plot.selectAll("path.background")
		.data([background_data])
	.enter().append("path")
		.style("fill", "black")
		.style("fill-opacity", 0.2)
		.style("stroke-opacity",0.2)
		.style("stroke", "black")
		.attr("class", "area")
		.attr("d", area);
	plot.append("svg:path").attr("d", median(background_data))
		.style("stroke","black")
		.style("stroke-opacity", 0.5);
	
	// Plot coordinate data 
	plot.selectAll("path.coordinate")
		.data([coord_data])
	.enter().append("path")
		.style("fill", "red")
		.style("fill-opacity", 0.2)
		.style("stroke-opacity",0.2)
		.style("stroke", "red")
		.attr("class", "area")
		.attr("d", area);
	plot.append("svg:path").attr("d", median(coord_data))
		.style("stroke","red")
		.style("stroke-opacity", 0.5);

}
