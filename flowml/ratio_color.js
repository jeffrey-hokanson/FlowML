function ratio_color(elemId, value, min, max){

	var width = 50;
	var height = 25;

	var plot = d3.select(elemId)
			.attr('width', width)
			.attr('height', height);

	plot.append("rect");
	var square = plot.append("svg:rect")
		.attr('x',0)
		.attr('y',0)
		.attr('fill','blue')
		.attr('width', width)
		.attr('height', height);

	plot.append('text')
		.attr('x',width/2)
		.attr('y',height/2)
		.attr('text-anchor', 'middle')
		.attr('alignment-baseline', 'middle')
		.text('hi');
}
