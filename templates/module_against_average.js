(function(){
    var width = 1100;
    var height = 600;

    var margin = {
        top: 40,
        bottom: 20,
        left: 60,
        right: 400,
    };

    var pformat = d3.format('.1%');

    var svg = d3.select("#agreement_evaluation_vis")
        .append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("xmlns", "http://www.w3.org/2000/svg")
            .style("font-family", '"tee_franklin_light", "Source Sans Pro", "Helvetica Neue",Helvetica,"Open Sans",Arial,sans-serif;');

    var legend = svg.append("g")
            .attr('class', 'legend')
            .attr('transform', 'translate(' + margin.left + ',' + margin.top/4 + ')');

    svg = svg.append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

    width = width - margin.left - margin.right;
    height = height - margin.top - margin.bottom;

    var xScale = d3.scaleLinear()
            .rangeRound([0, width]);

    var yScale = d3.scaleBand()
            .rangeRound([0, height])
            .padding(0.0);

    var colourScale = d3.scaleLinear()
        .range(["hsla(0, 60%, 50%, 1)", "hsla(45, 70%, 60%, 1)", "hsla(90, 50%, 50%, 1)"]);

    var yAxis = d3.axisRight(yScale);

    svg.append('g')
        .attr('class', 'y axis')
        .attr('transform', 'translate(' + width + ',0)');

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

    var module_data = d3.csvParse(d3.select('#data_agreement_comparison').html());

    module_data.forEach(function(d){
        d.module = +d.module;
        d.AllModules = +d.AllModules;
        d.diff = d.module - d.AllModules;
    })

    var questions = module_data.map(function(d) { return d.question; });

    yScale.domain(questions);
    xScale.domain([d3.min(module_data, function(d){
        return d.module < d.AllModules ? d.module : d.AllModules;
    }), 1.05]);
    colourScale.domain([d3.min(module_data, function(d){
        return d.diff;
    }), 0, d3.max(module_data, function(d){
        return d.diff;
    })]);

    var rows = svg.selectAll('.shading')
        .data(module_data)
        .enter()
        .append('rect')
        .attr('class', 'shading')
        .attr('x', -margin.left)
        .attr('width', width+margin.left)
        .attr('y', function(d){
            return yScale(d.question);
        })
        .attr('height', yScale.bandwidth())
        .attr('fill', function(d, i){
            if(i % 2 == 0) {
                return '#ddd';
            } else {
                return '#fff';
            }
        })
        .attr('opacity', function(d, i){
            if(i % 2 == 0) {
                return 0.2;
            } else {
                return 1;
            }
        });

    var lines = svg.selectAll('.lines')
        .data(module_data)
        .enter()
        .append('path')
        .attr('d', function(d){
            var height = yScale(d.question)+yScale.bandwidth()/2;
            var end_point = [d.diff > 0 ? xScale(d.module)-5: xScale(d.module)+5, height];
            var start_point = [xScale(d.AllModules), height];
            var main_line = "M" + end_point[0] + "," + end_point[1] + " L" + start_point[0] + "," + start_point[1];
            if(d.diff > 0) {
                //arrow points right
                var arrowX = end_point[0] - 10;
            } else {
                //arrow points left
                var arrowX = end_point[0] + 10;
            }
            var upper = "M" + end_point[0] + "," + end_point[1] + " L" + arrowX + "," + (height-5);
            var lower = "M" + end_point[0] + "," + end_point[1] + " L" + arrowX + "," + (height+5);
            return main_line + " " + upper + " " + lower;
        })
        .attr('stroke', 'black')
        .attr('stroke-width', '0.5px');

    var diamond = d3.symbol()
      .type(d3.symbolDiamond)
      .size(80);

    legend
        .append('path')
        .attr('d', diamond())
        .attr('fill', '#eee')
        .attr('stroke', 'black')
        .attr('stroke-width', '0.5px');

    legend
        .append('text')
        .attr('dx', '0.8em')
        .attr('dy', '0.25em')
        .text('School average');

    legend
        .append('circle')
        .attr('cx', 200)
        .attr('cy',0)
        .attr('r', 5)
        .attr('fill', 'hsla(90, 50%, 50%, 1)');

    legend
        .append('text')
        .attr('x', 200)
        .attr('y', 0)
        .attr('dx', '0.8em')
        .attr('dy', '0.25em')
        .text('Module score');

    var averages = svg.selectAll('.average')
        .data(module_data)
        .enter()
        .append('g')
        .attr('class', 'average')
        .attr('transform', function(d){
            return 'translate(' + xScale(d.AllModules) + ',' + (yScale(d.question)+yScale.bandwidth()/2) + ')';
        })
        .append('path')
        .attr('d', diamond())
        .attr('fill', '#eee')
        .attr('stroke', 'black')
        .attr('stroke-width', '0.5px');

    var scores = svg.selectAll('.scores')
        .data(module_data)
        .enter()
        .append('circle')
        .attr('class', 'scores')
        .style('fill', function(d, i){
            return colourScale(d.diff);
        })
        .attr('cx', function(d){
            return xScale(d.module);
        })
        .attr('cy', function(d){
            return yScale(d.question)+yScale.bandwidth()/2;
        })
        .attr('r', 5);

    var labels = svg.selectAll('.labels')
        .data(module_data)
        .enter()
        .append('g')
        .attr('class', 'label')

    labels
        .append('text')
        .attr('x', function(d){
            return xScale(d.AllModules);
        })
        .attr('y', function(d){
            return yScale(d.question)+yScale.bandwidth()/2;
        })
        .attr('text-anchor', function(d){
            if(d.diff < 0) {
                return 'start';
            } else {
                return 'end';
            }
        })
        .attr('dx', function(d){
            if(d.diff < 0) {
                return '0.5em';
            } else {
                return '-0.5em';
            }
        })
        .attr('dy', '0.25em')
        .text(function(d){
            return pformat(d.AllModules);
        });

    labels
        .append('text')
        .attr('x', function(d){
            return xScale(d.module);
        })
        .attr('y', function(d){
            return yScale(d.question)+yScale.bandwidth()/2;
        })
        .attr('text-anchor', function(d){
            if(d.diff < 0) {
                return 'end';
            } else {
                return 'start';
            }
        })
        .attr('dx', function(d){
            if(d.diff < 0) {
                return '-0.5em';
            } else {
                return '0.5em';
            }
        })
        .attr('fill', function(d){
            return colourScale(d.diff);
        })
        .attr('dy', '0.25em')
        .text(function(d){
            return pformat(d.module);
        });

        svg.select('.y.axis')
            .call(yAxis)
            .selectAll(".tick text")
            .attr('font-size', '12px')
            .call(wrap, margin.right);

})();
