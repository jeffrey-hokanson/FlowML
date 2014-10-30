function ratio_color(elemId, value){
	/*  
	 *
	 */
	var width = 50;
	var height = 25;

	// Colorbrewer RdYlBu-11
	//var colors = ["#a50026","#d73027","#f46d43","#fdae61","#fee090","#ffffbf","#e0f3f8","#abd9e9","#74add1","#4575b4","#313695"]
	// Colorbrewer RdBu-9
	//var colors = ["#b2182b","#d6604d","#f4a582","#fddbc7","#f7f7f7","#d1e5f0","#92c5de","#4393c3","#2166ac"]
	var colors = ["#b2182b","#ef8a62","#fddbc7","#f7f7f7","#d1e5f0","#67a9cf","#2166ac"];
	var colormap = d3.scale.log()
		    .domain([1e-3, 1e-2, 1e-1, 1, 1e1, 1e2, 1e3 ])
			.range(colors)
			.interpolate(d3.interpolateHcl);


	var plot = d3.select(elemId)
			.attr('width', width)
			.attr('height', height);

	plot.append("rect");
	var square = plot.append("svg:rect")
		.attr('x',0)
		.attr('y',0)
		.attr('fill',colormap(1/value))
		.attr('width', width)
		.attr('height', height);


	var num_str = value.toExponential(1);
	
	// Pretty formatting of ratio number
	/*
	var num_str = value.toExponential(1)
		.replace('e','10<tspan baseline-shift="super">')
		.concat('</tspan>');
	num_str = "<tspan>".concat(num_str)
			.concat("</tspan>");
	*/

	plot.append('text')
		.attr('x',width/2)
		.attr('y',height/2)
		.attr('text-anchor', 'middle')
		.attr('alignment-baseline', 'middle')
		.text(num_str);
}
