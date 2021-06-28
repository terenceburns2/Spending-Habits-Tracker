// Makes a chart object storing many of the graph critical information
function constructGraph(div_name, width = 540, height = 300)
{
	var graph = {
		width: width,
		height: height,
		margin: {top: 10, right: 30, bottom: 30, left: 60},
		div_name: div_name,
		svg: "undefined",
		data: new Array()
	}
	
	graph.width = width - graph.margin.left + graph.margin.right;
	graph.height = height - graph.margin.top + graph.margin.bottom;
	
	return graph;
}

// Adds data and a link for a category to the given graph
function addDateValue(graph, date, value)
{
	var new_data = new Object();
	
	new_data["date"] = d3.timeParse('%Y-%m-%d')(date);
	new_data["value"] = value;
	
	graph.data.push(new_data);
}

// Removes all the data from the chart
function emptyGraphData(graph)
{
	graph.data = new Object();
}

// Displays and flushes the line graph to the interface
function displayGraph(graph)
{
	graph.svg = d3.select(graph.div_name)
	  .append("svg")
		.attr("width", graph.width + graph.margin.left + graph.margin.right)
		.attr("height", graph.height + graph.margin.top + graph.margin.bottom)
	  .append("g")
		.attr("transform",
			  "translate(" + graph.margin.left + "," + graph.margin.top + ")");
	
	var x = d3.scaleTime()
      .domain(d3.extent(graph.data, function(d) { return d.date; }))
      .range([ 0, graph.width ]);
    graph.svg.append("g")
      .attr("transform", "translate(0," + graph.height + ")")
      .call(d3.axisBottom(x));
	  
	var y = d3.scaleLinear()
      .domain([0, d3.max(graph.data, function(d) { return +d.value; })])
      .range([ graph.height, 0 ]);
    graph.svg.append("g")
      .call(d3.axisLeft(y));
	  
	graph.svg.append("path")
      .datum(graph.data)
      .attr("fill", "none")
      .attr("stroke", "#d03027")
      .attr("stroke-width", 4)
      .attr("d", d3.line()
        .x(function(d) { return x(d.date) })
        .y(function(d) { return y(d.value) })
        )
}
