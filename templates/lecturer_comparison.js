(function(){

    console.log(module_data_list);
    var width = 1100;
    var height = 600;

    var margin = {
        top: 40,
        bottom: 20,
        left: 0,
        right: 400,
    };

    var pformat = d3.format('.1%');

    var svg = d3.select("#overall_evaluation_vis")
        .append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("xmlns", "http://www.w3.org/2000/svg")
            .style("font-family", '"tee_franklin_light", "Source Sans Pro", "Helvetica Neue",Helvetica,"Open Sans",Arial,sans-serif;');

    var legend = svg.append('g')
            .attr('class', 'legend')

    svg = svg.append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

    width = width - margin.left - margin.right;
    height = height - margin.top - margin.bottom;

    var xScale = d3.scaleLinear()
            .domain([0, 1])
            .rangeRound([0, width]);

    var yScale = d3.scaleBand()
            .rangeRound([0, height])
            .padding(0.1);

    var colourScale = d3.scaleOrdinal()
        .domain(['N/A', 'Disagree', 'Neither Agree nor Disagree', 'Agree'])
        .range(["#222", "hsla(0, 60%, 50%, 1)", "hsla(45, 70%, 60%, 1)", "hsla(90, 50%, 50%, 1)"]);

    var yAxis = d3.axisRight(yScale);

    svg.append('g')
        .attr('class', 'y axis')
        .attr('transform', 'translate(' + width + ', 0)');

    legend.selectAll('.bar')
        .data(colourScale.domain())
        .enter()
        .append('rect')
        .attr('x', function(d, i){
            return margin.left + (width/4) * i;
        })
        .attr('y', 30)
        .attr('height', 20)
        .attr('width', width/4)
        .attr('fill', function(d){
            return colourScale(d);
        })
        .attr('stroke', '#333')
        .attr('stroke-width', '0.5px')

    legend.selectAll('.bar')
        .data(colourScale.domain())
        .enter()
        .append('rect')
        .attr('x', function(d, i){
            return margin.left + (width/4) * i;
        })
        .attr('y', 51)
        .attr('height', 10)
        .attr('width', width/4)
        .attr('fill', function(d){
            return colourScale(d);
        })
        .attr('opacity', 0.5)
        .attr('stroke', '#333')
        .attr('stroke-width', '0.5px')

    legend.selectAll('.label')
        .data(colourScale.domain())
        .enter()
        .append('text')
        .attr('x', function(d, i){
            return margin.left + width/8 * ((2 * i) + 1);
        })
        .attr('text-anchor', 'middle')
        .attr('y', 45)
        .text(function(d){
            return d;
        })
        .attr('fill', '#eee');

    legend.selectAll('.averagelabel')
        .data(['Average over all modules'])
        .enter()
        .append('text')
        .attr('x', width/2)
        .attr('text-anchor', 'middle')
        .attr('font-size', '9px')
        .attr('fill', '#333')
        .attr('y', 59)
        .text(function(d){
            return d;
        });

    function wrap(text, width) {
        text.each(function() {
            var text = d3.select(this);
            var words = text.text().split(/\s+/).reverse();
            var word;
            var line = [];
            var lineNumber = 0;
            var lineHeight = 1.1;
            var y = text.attr("y");
            var x = text.attr("x");
            var dy = parseFloat(text.attr("dy"));
            var dx = parseFloat(text.attr("dx"));
            var tspan = text.text(null)
                .append("tspan")
                .attr("x", x)
                .attr("y", y)
                .attr("dy", dy + "em");
            while (word = words.pop()) {
                line.push(word);
                tspan.text(line.join(" "));
                if (tspan.node().getComputedTextLength() > width-x) {
                    line.pop();
                    tspan.text(line.join(" "));
                    line = [word];
                    tspan = text.append("tspan")
                        .attr("x", x)
                        .attr("y", y)
                        .attr("dy", ++lineNumber * lineHeight + dy + "em")
                        .text(word);
                }
            }
        });
    }

    var all_modules = d3.csvParse(d3.select('#data_average').html());
    var ind_mod = d3.csvParse(d3.select('#data_module').html());

    var columns = all_modules.columns.splice(1)

    var questions = all_modules.map(function(d) { return d.question; });
    var labels = []
    labels.push(0);
    questions.forEach(function(q, i) {
        labels.push(i + 1);
        labels.push(q);
        labels.push(q + 'Average');
    });


    all_modules.forEach(function(d){
        d.question = d.question + 'Average';
    });

    yScale.domain(labels);
    yAxis.tickValues(questions);

    var stack = d3.stack()
        .keys(columns);

    var all_data = all_modules.concat(ind_mod);

    var stackedData = stack(all_data);

    var g = svg.selectAll('g.series')
        .data(stackedData)
        .enter()
        .append('g')
        .attr('class', 'series')
        .style('fill', function(d, i){
            return colourScale(columns[i])
        });

    g.selectAll('rect')
        .data(function(d) {
            return d;
        })
        .enter()
        .append('rect')
        .attr('width', function(d) {
            return xScale(d[1]) - xScale(d[0]);
        })
        .attr('x', function(d) {
            return xScale(d[0]);
        })
        .attr('y', function(d, i) {
            return yScale(d.data.question);
        })
        .attr('height', function(d){
            if(d.data.question.includes('Average')) {
                return 0.6 * yScale.bandwidth();
            } else {
                return yScale.bandwidth();
            }
        })
        .attr('stroke', '#333')
        .attr('stroke-width', '0.5px')
        .attr('opacity', function(d, i){
            if(d.data.question.includes('Average')) {
                return 0.5
            } else {
                return 1;
            }
        });

    g.selectAll('.label')
        .data(function(d) {
            return d;
        })
        .enter()
        .append('text')
        .attr('fill', function(d){
            if(d){
                if(d.data.question.includes('Average')){
                    return '#666';
                } else {
                    return '#eee';
                }
            }
        })
        .attr('font-size', function(d){
            if(d){
                if(d.data.question.includes('Average')){
                    return '8px';
                } else {
                    return '12px';
                }
            }
        })
        .attr('text-anchor', 'middle')
        .text(function(d){
            var width = (xScale(d[1]) - xScale(d[0]));
            if (width < 40) {
                return '';
            } else {
                return pformat(d[1] - d[0]);
            }
        })
        .attr('x', function(d){
            return xScale(d[0]) + ((xScale(d[1]) - xScale(d[0])) / 2);
        })
        .attr('y', function(d, i) {
            return yScale(d.data.question);
        })
        .attr('dy', '0.8em')

        svg.select('.y.axis')
            .call(yAxis)
            .selectAll(".tick text")
            .attr('font-size', '12px')
            .call(wrap, margin.right);

})();
