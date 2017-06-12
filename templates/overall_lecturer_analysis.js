function horizontalRankingChart() {

    var width = 1300;
    var height = 600;

    var margin = {
        top: 80,
        bottom: 60,
        left: 200,
        right: 200,
    };

    var label_margin = 100;

    var pformat = d3.format('.1%');

    var average_value;

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

    var colourScale = d3.scaleLinear()
        .range(["hsla(0, 60%, 50%, 1)", "hsla(45, 70%, 60%, 1)", "hsla(90, 50%, 50%, 1)"]);

    function chart(selection) {
        selection.each(function(data) {

            var svg = d3.select(this)
                .append('svg')
                .attr('width', width)
                .attr('height', height);

            var legend = svg.append("g")
                .attr('class', 'legend')
                .attr('transform', 'translate(' + margin.left + ',' + margin.top / 2 + ')');

            svg = svg.append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            width = width - margin.left - margin.right;
            height = height - margin.top - margin.bottom;

            var xScale = d3.scaleLinear()
                .range([width, 0])

            svg.append('g')
                .attr('class', 'labels');

            var minimum = d3.min(data, function(d) {
                return d.value < average_value ? d.value : d.average;
            });

            xScale.domain([minimum, 1.05]);

            colourScale.domain([d3.min(data, function(d) {
                return d.diff;
            }), 0, d3.max(data, function(d) {
                return d.diff;
            })]);

            data.forEach(function(d) {
                d.x = xScale(d.value);
                d.labelX = xScale(d.value);
            });

            relax(data);

            var diamond = d3.symbol()
                .type(d3.symbolDiamond)
                .size(160);

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
                .attr('cy', 0)
                .attr('r', 5)
                .attr('fill', 'hsla(90, 50%, 50%, 1)');

            legend
                .append('text')
                .attr('x', 200)
                .attr('y', 0)
                .attr('dx', '0.8em')
                .attr('dy', '0.25em')
                .text('Lecturer score');

            legend
                .append('path')
                .attr('d', 'M ' + xScale(1) + ' ' + (height + 30) + ' L ' + width + ' ' + (height + 30) +
                    'M ' + xScale(1) + ' ' + (height + 40) + 'L ' + xScale(1) + ' ' + (height + 20) +
                    'M ' + width + ' ' + (height + 40) + 'L ' + width + ' ' + (height + 20))
                .attr('stroke', 'black')
                .attr('stroke-width', '0.5px');

            legend
                .append('text')
                .attr('x', xScale(1))
                .attr('y', (height + 60))
                .attr('text-anchor', 'middle')
                .text('Highest')

            legend
                .append('text')
                .attr('x', width)
                .attr('y', (height + 60))
                .attr('text-anchor', 'middle')
                .text('Lowest')

            legend
                .append('text')
                .attr('x', width / 2)
                .attr('y', (height + 80))
                .attr('text-anchor', 'middle')
                .attr('font-weight', 'bold')
                .text('Percentage Agreement')

            var averages = svg.selectAll('.average')
                .data([average_value])
                .enter()
                .append('g')
                .attr('class', 'average')
                .attr('transform', function(d) {
                    return 'translate(' + xScale(d) + ',' + (height - 30) + ')';
                })
                .append('path')
                .attr('d', diamond())
                .attr('fill', '#eee')
                .attr('stroke', 'black')
                .attr('stroke-width', '0.5px');

            var scores = svg.selectAll('.scores')
                .data(data)
                .enter()
                .append('circle')
                .attr('class', 'scores')
                .style('fill', function(d, i) {
                    return colourScale(d.diff);
                })
                .attr('cx', function(d) {
                    return xScale(d.value);
                })
                .attr('cy', function(d) {
                    return height - 30;
                })
                .attr('r', 5);

            var labelg = svg.append('g')
                .attr('transform', 'translate(0, ' + height + ')')

            var labels = labelg.selectAll('.label')
                .data(data)
                .enter()
                .append('g')
                .attr('transform', function(d) {
                    return 'translate(' + d.labelX + ',' + (-label_margin) + ')';
                })
                .append('text')
                .attr('class', 'label')
                .attr('text-anchor', 'start')
                .attr('transform', 'rotate(-45)')
                .text(function(d) {
                    return (d.lecturer);
                });

            var polylines = svg.selectAll(".lines")
                .data(data);

            polylines.enter()
                .append("polyline")
                .attr("points", function(d) {
                    var start = [
                        xScale(d.value), height - 35
                    ];
                    var midpoint = [
                        xScale(d.value), ((height - 35) - ((label_margin - 35) / 2)),
                    ];
                    var end = [
                        d.labelX, height - label_margin + 2,
                    ];
                    return [start, midpoint, end];
                });

        });
    }

    chart.label_margin = function(_) {
        if (!arguments.length) return label_margin;
        label_margin = _;
        return chart;
    }

    chart.average_value = function(_) {
        if (!arguments.length) return average_value;
        average_value = _;
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
