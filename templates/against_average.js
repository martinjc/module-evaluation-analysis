function againstAverage() {

    var width = 1100;
    var height = 300;

    var margin = {
        top: 40,
        bottom: 20,
        left: 20,
        right: 200,
    };

    var pformat = d3.format('.1%');

    var svg;
    var legend;

    var value_label;

    var averages;

    var colourScale = d3.scaleLinear()
        .range(["hsla(0, 60%, 50%, 1)", "hsla(45, 70%, 60%, 1)", "hsla(90, 50%, 50%, 1)"]);

    function wrap(text, width) {
        text.each(function() {
            var text = d3.select(this);
            var words = text.text()
                .split(/\s+/)
                .reverse();
            var word;
            var line = [];
            var lineNumber = 0;
            var lineHeight = 1.1;
            var y = text.attr("y");
            var x = text.attr("x");
            var dy = parseFloat(text.attr("dy") || 0);
            var dx = parseFloat(text.attr("dx") || 0);
            var tspan = text.text(null)
                .append("tspan")
                .attr("x", x)
                .attr("y", y)
            while (word = words.pop()) {
                line.push(word);
                tspan.text(line.join(" "));
                if (tspan.node()
                    .getComputedTextLength() > width - x) {
                    line.pop();
                    tspan.text(line.join(" "));
                    line = [word];
                    tspan = text.append("tspan")
                        .attr("x", x)
                        .attr("y", y)
                        .attr("dy", "1em")
                        .attr("dx", dx + "em")
                        .text(word);
                    lineNumber += 1
                }
            }
            if (lineNumber > 0) {
                text.attr('dy', (-1 * ((lineNumber / 2) - .25)) + "em");
            }
        });
    }

    function relax(data) {
        var spacing = 20;
        var dx = 1;
        var repeat = false;
        data.forEach(function(dA, i) {
            var xA = dA.labelX;
            data.forEach(function(dB, j) {
                var xB = dB.labelX
                if (i === j) {
                    return;
                }
                diff = xA - xB;
                if (Math.abs(diff) > spacing) {
                    return;
                }
                repeat = true;
                magnitude = diff > 0 ? 1 : -1;
                adjust = magnitude * dx;
                dA.labelX = +xA + adjust;
                dB.labelX = +xB - adjust;
            })
        })
        if (repeat) {
            relax(data);
        }
    }

    function chart(selection) {
        selection.each(function(data) {
            svg = d3.select(this)
                .append("svg")
                .attr("width", width)
                .attr("height", height);

            legend = svg.append("g")
                .attr('class', 'legend')
                .attr('transform', 'translate(' + margin.left + ',' + margin.top / 4 + ')');

            svg = svg.append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

            width = width - margin.left - margin.right;
            height = height - margin.top - margin.bottom;

            var xScale = d3.scaleLinear()
                .rangeRound([0, width]);

            var yScale = d3.scaleBand()
                .rangeRound([0, height])
                .padding(0.0);
            var yAxis = d3.axisRight(yScale);

            svg.append('g')
                .attr('class', 'y axis')
                .attr('transform', 'translate(' + width + ',0)');

            var questions = data.map(function(d) {
                return d.question;
            });

            yScale.domain(questions);

            xScale.domain([-0.1, 1.1]);

            colourScale.domain([
                d3.min(data, function(d) {
                    return d.diff;
                }), 0, d3.max(data, function(d) {
                    return d.diff;
                })
            ]);

            var rows = svg.selectAll('.shading')
                .data(data)
                .enter()
                .append('rect')
                .attr('class', 'shading')
                .attr('x', -margin.left)
                .attr('width', width + margin.left)
                .attr('y', function(d) {
                    return yScale(d.question);
                })
                .attr('height', yScale.bandwidth())
                .attr('fill', function(d, i) {
                    if (i % 2 == 0) {
                        return '#ddd';
                    } else {
                        return '#fff';
                    }
                })
                .attr('opacity', function(d, i) {
                    if (i % 2 == 0) {
                        return 0.2;
                    } else {
                        return 1;
                    }
                });

            var lines = svg.selectAll('.lines')
                .data(data)
                .enter()
                .append('path')
                .attr('d', function(d) {
                    var height = yScale(d.question) + yScale.bandwidth() / 2;
                    var end_point = [d.diff > 0 ? xScale(d.Agree) - 5 : xScale(d.Agree) + 5, height];
                    var start_point = [xScale(d.average), height];
                    var main_line = "M" + end_point[0] + "," + end_point[1] + " L" + start_point[0] + "," + start_point[1];
                    if (d.diff > 0) {
                        //arrow points right
                        var arrowX = end_point[0] - 10;
                    } else {
                        //arrow points left
                        var arrowX = end_point[0] + 10;
                    }
                    var upper = "M" + end_point[0] + "," + end_point[1] + " L" + arrowX + "," + (height - 5);
                    var lower = "M" + end_point[0] + "," + end_point[1] + " L" + arrowX + "," + (height + 5);
                    return main_line + " " + upper + " " + lower;
                })
                .attr('stroke', 'black')
                .attr('stroke-width', '0.5px');

            var this_legend = legend
                .append('g')
                .attr('transform', 'translate(' + (20 + (averages.length * 150)) + ',0)');

            this_legend
                .append('circle')
                .attr('cx', 0)
                .attr('cy', 0)
                .attr('r', 5)
                .attr('fill', 'hsla(90, 50%, 50%, 1)')
                .attr('stroke', 'black')
                .attr('stroke-width', '0.5px');

            this_legend
                .append('text')
                .attr('dx', '0.8em')
                .attr('dy', '0.25em')
                .text(value_label);

            averages.forEach(function(a, i) {
                var name = a.name;
                var title = a.title;
                var symbol = a.symbol;
                var averages = svg.selectAll('.average_' + name)
                    .data(a.data)
                    .enter()
                    .append('g')
                    .attr('class', 'average')
                    .attr('transform', function(d) {
                        return 'translate(' + xScale(d.average) + ',' + (yScale(d.question) + yScale.bandwidth() / 2) + ')';
                    })
                    .append('path')
                    .attr('d', symbol)
                    .attr('fill', a.fill)
                    .attr('stroke', 'black')
                    .attr('stroke-width', '0.5px');

                var this_legend = legend
                    .append('g')
                    .attr('transform', 'translate(' + (20 + (i * 150)) + ',0)');
                this_legend
                    .append('path')
                    .attr('d', symbol)
                    .attr('fill', a.fill)
                    .attr('stroke', 'black')
                    .attr('stroke-width', '0.5px');
                this_legend
                    .append('text')
                    .attr('dx', '0.8em')
                    .attr('dy', '0.25em')
                    .text(title);
            });

            var scores = svg.selectAll('.scores')
                .data(data)
                .enter()
                .append('circle')
                .attr('class', 'scores')
                .style('fill', function(d, i) {
                    return colourScale(d.diff);
                })
                .attr('cx', function(d) {
                    return xScale(d.Agree);
                })
                .attr('cy', function(d) {
                    return yScale(d.question) + yScale.bandwidth() / 2;
                })
                .attr('r', 5)
                .attr('stroke', 'black')
                .attr('stroke-width', '0.5px');

            var labels = svg.selectAll('.labels')
                .data(data)
                .enter()
                .append('g')
                .attr('class', 'label')

            labels
                .append('text')
                .attr('x', function(d) {
                    return xScale(d.average);
                })
                .attr('y', function(d) {
                    return yScale(d.question) + yScale.bandwidth() / 2;
                })
                .attr('text-anchor', function(d) {
                    if (d.diff < 0) {
                        return 'start';
                    } else {
                        return 'end';
                    }
                })
                .attr('dx', function(d) {
                    if (d.diff < 0) {
                        return '0.2em';
                    } else {
                        return '-0.2em';
                    }
                })
                .attr('fill', '#4169e1')
                .attr('dy', '-0.35em')
                .text(function(d) {
                    return pformat(d.average);
                });

            labels
                .append('text')
                .attr('x', function(d) {
                    return xScale(d.Agree);
                })
                .attr('y', function(d) {
                    return yScale(d.question) + yScale.bandwidth() / 2;
                })
                .attr('text-anchor', function(d) {
                    if (d.diff < 0) {
                        return 'end';
                    } else {
                        return 'start';
                    }
                })
                .attr('dx', function(d) {
                    if (d.diff < 0) {
                        return '-0.2em';
                    } else {
                        return '0.2em';
                    }
                })
                .attr('fill', function(d) {
                    return colourScale(d.diff);
                })
                .attr('dy', '-0.35em')
                .text(function(d) {
                    return pformat(d.Agree);
                });

            svg.select('.y.axis')
                .call(yAxis)
                .selectAll(".tick text")
                .attr('font-size', '12px')
                .call(wrap, margin.right);

        });
    }

    chart.averages = function(_) {
        if (!arguments.length) return averages;
        averages = _;
        return chart;
    }

    chart.value_label = function(_) {
        if (!arguments.length) return value_label;
        value_label = _;
        return chart;
    }

    chart.margin = function(_) {
        if (!arguments.length) return margin;
        margin = _;
        return chart;
    };

    chart.width = function(_) {
        if (!arguments.length) return width;
        width = _;
        return chart;
    };

    chart.height = function(_) {
        if (!arguments.length) return height;
        height = _;
        return chart;
    };

    return chart;
}
