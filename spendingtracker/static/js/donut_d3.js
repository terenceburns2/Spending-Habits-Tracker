// Makes a chart object storing many of the chart critical information
function constructChart(div_name, width = 400, height = 400, margin = 100)
{
	var chart = {
		width: width,
		height: height,
		margin: margin,
		radius: Math.min(width, height) / 2 - margin,
		div_name: div_name,
		svg: "undefined",
		data: new Object(),
		functions: new Object()
	}

	return chart;
}

// Adds data and a link for a category to the given pie chart
function addCategoryData(chart, category_name, category_data, category_function)
{
	if (chart.data[category_name] == null) {
		chart.data[category_name] = category_data;
	} else {
		chart.data[category_name] = chart.data[category_name] + category_data;
	}
	chart.functions[category_name] = category_function;
}

// Removes data for a category on the given chart
function removeCategoryData(chart, category_name)
{
	delete chart.data[category_name];
	delete chart.functions[category_name];
}

// Removes all the data from the chart
function emptyChartData(chart)
{
	chart.data = new Object();
	chart.functions = new Object();
}

function removePreviousChart() {
	d3.select('svg').remove();
}

// Sets what happens when a user clicks on a pie chart slice
function clickOnSlice(chart, d)
{
	chart.functions[d.data.key]();
}

// Sets what happens when a user hovers the cursor on a pie chart slice
function mouseOverSlice(chart, d)
{
	document.body.style.cursor = "pointer";
}

// Sets what happens when a user hovers off the cursor on a pie chart slice
function mouseOutSlice(chart, d)
{
	document.body.style.cursor = "default";
}

// Displays and flushes the pie chart to the interface
function displayChart(chart)
{
	// If chart already made, transition from old chart to new chart
	if (chart.svg != "undefined")
	{
		var svg = d3.select(chart.div_name);
		svg.selectAll("*").remove();
	}
	
	// Filters out entries that make up less than 10%
	var keys = Object.keys(chart.data);
	var values = Object.values(chart.data);
	
	var total = 0;
	for (let i = 0; i < values.length; i++)
	{
		total += values[i];
	}
	
	var data = new Object();
	for (let i = 0; i < keys.length; i++)
	{
		if (values[i] / total >= 0.05)
		{
			data[keys[i]] = values[i];
		}
	}

	// Set the color scale
	var color = d3.scaleOrdinal()
	  .domain(data)
	  .range(["#9a65b7", "#c62355", "#6fba12", "#243cb9", "#67e3df", "#7b5452"]);

	// Compute the position of each group on the pie:
	chart.pie = d3.pie()
	  .value(function(d) {return d.value; })

	chart.arc = d3.arc()
		.innerRadius(chart.radius * 0.65)
		.outerRadius(chart.radius)

	// Begins setting up the pie chart
	chart.svg = d3.select(chart.div_name)
		  .append("svg")
			.attr("width", chart.width)
			.attr("height", chart.height)
		  .append("g")
			.attr("transform", "translate(" + chart.width / 2 + "," + chart.height / 2 + ")");

	var div = d3.select("body").append("div")
		.attr("class", "donutHoverBox")
		.style("opacity", 0);

	// Build the pie chart: Basically, each part of the pie is a path that we build using the arc function.
	chart.svg
	  .selectAll('whatever')
	  .data(chart.pie(d3.entries(data)))
	  .enter()
	  .append('path')
	  .attr('d', chart.arc)
	  .attr('fill', function(d){ return(color(d.data.key)); })
	  .attr("stroke", "black")
	  .style("stroke-width", "0px")
	  .on("click", function(d){ clickOnSlice(chart, d); })
	  // .on("mouseover", function(d){ mouseOverSlice(chart, d); })
	  // .on("mouseout", function(d){mouseOutSlice(chart, d); })
	  .on("mouseover", function(d) {
		  d3.select(this).transition()
			  .duration('50')
			  .attr('opacity', '.50');
		  //Adds div holding data when the user moves mouse away
          div.transition()
               .duration(50)
               .style("opacity", 1);
          div.html("£"+d.value.toFixed(2))
			   .style("left", (d3.event.pageX + 10) + "px")
			   .style("top", (d3.event.pageY - 15) + "px");
	  })
	  .on("mouseout", function() {
		  d3.select(this).transition()
			  .duration('50')
			  .attr('opacity', '1');
		  //Remove div holding data when the user moves mouse away
          div.transition()
               .duration('50')
               .style("opacity", 0);
	  });

	addLabels(chart, data);
}

// Adds the labels elements to the pie chart
function addLabels(chart, data)
{
    let outerArc = d3.arc()
        .innerRadius(chart.radius * 0.9)
        .outerRadius(chart.radius * 0.9);

	// Adds the lines that connect the label text and pie chart segments
    chart.svg
        .selectAll('allPolylines')
        .data(chart.pie(d3.entries(data)))
        .enter()
        .append('polyline')
        .attr("stroke", "black")
        .style("fill", "none")
        .attr("stroke-width", 1)
        .attr('points', function(d) {
            let posA = chart.arc.centroid(d) ;// line insertion in the slice
            let posB = outerArc.centroid(d); // line break: we use the other arc generator that has been built only for that
            let posC = outerArc.centroid(d); // Label position = almost the same as posB
            let midangle = d.startAngle + (d.endAngle - d.startAngle) / 2; // we need the angle to see if the X position will be at the extreme right or extreme left
            posC[0] = chart.radius * 0.95 * (midangle < Math.PI ? 1 : -1); // multiply by 1 or -1 to put it on the right or on the left
            return [posA, posB, posC]
        });

    // Adds the label text
    chart.svg
        .selectAll('allLabels')
        .data(chart.pie(d3.entries(data)))
        .enter()
        .append('text')
        .text( function(d) { console.log(d.data.key) ; return d.data.key } )
        .attr('transform', function(d) {
            let pos = outerArc.centroid(d);
            let midangle = d.startAngle + (d.endAngle - d.startAngle) / 2;
            pos[0] = chart.radius * 0.99 * (midangle < Math.PI ? 1 : -1);
            return 'translate(' + pos + ')';
        })
        .style('text-anchor', function(d) {
            let midangle = d.startAngle + (d.endAngle - d.startAngle) / 2;
            return (midangle < Math.PI ? 'start' : 'end')
        });
}