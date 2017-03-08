(function() {

    var margin = {
        top: 50,
        bottom: 20,
        left: 10,
        right: 10,
    };

    var label_margin_left = 100;

    var pformat = d3.format('.1%');

    var questions = [
        ': Was good at explaining things.',
        ': Was available when needed.',
        ': Made the subject interesting.'
    ];

    average_data = d3.csvParseRows(d3.select('#lecturer_average')
        .html(),
        function(d) {
            return {
                question: d[0],
                value: +d[1]
            };
        });
    average = {

    }
    average_data.forEach(function(d) {
        average[d.question] = d.value;
    });
    lecturer_data = d3.csvParse(d3.select('#lecturer_comparison')
        .html());
    lecturer_count = d3.csvParseRows(d3.select('#lecturer_count')
        .html(),
        function(d) {
            return {
                lecturer: d[0],
                count: +d[1]
            };
        });

    questions.forEach(function(q, i) {

        var width = 400;
        var height = 800;

        var svg = d3.select('#q' + i)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .attr("xmlns", "http://www.w3.org/2000/svg")
            .style("font-family", '"tee_franklin_light", "Source Sans Pro", "Helvetica Neue",Helvetica,"Open Sans",Arial,sans-serif;');

        var legend = svg.append("g")
            .attr('class', 'legend')
            .attr('transform', 'translate(' + margin.left + ',' + margin.top / 4 + ')');

        svg = svg.append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        width = width - margin.left - margin.right;
        height = height - margin.top - margin.bottom;

        svg.append('g')
            .attr('class', 'labels')

        var yScale = d3.scaleLinear()
            .range([height, 0])

        var colourScale = d3.scaleLinear()
            .range(["hsla(0, 60%, 50%, 1)", "hsla(45, 70%, 60%, 1)", "hsla(90, 50%, 50%, 1)"]);

        var average_value = average[q];

        var question_data = lecturer_data.map(function(d) {
            return {
                'lecturer': d.lecturer,
                'value': +d[q],
                'diff': (+d[q]) - average_value
            };
        });

        yScale.domain([d3.min(question_data, function(d) {
            return d.value < average_value ? d.value : d.average;
        }), 1.05]);
        colourScale.domain([d3.min(question_data, function(d) {
            return d.diff;
        }), 0, d3.max(question_data, function(d) {
            return d.diff;
        })]);

        question_data.forEach(function(d) {
            d.y = yScale(d.value);
            d.starty = yScale(d.value);
        });

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

        var averages = svg.selectAll('.average')
            .data([average_value])
            .enter()
            .append('g')
            .attr('class', 'average')
            .attr('transform', function(d) {
                return 'translate(30,' + yScale(d) + ')';
            })
            .append('path')
            .attr('d', diamond())
            .attr('fill', '#eee')
            .attr('stroke', 'black')
            .attr('stroke-width', '0.5px');

        var scores = svg.selectAll('.scores')
            .data(question_data)
            .enter()
            .append('circle')
            .attr('class', 'scores')
            .style('fill', function(d, i) {
                return colourScale(d.diff);
            })
            .attr('cy', function(d) {
                return yScale(d.value);
            })
            .attr('cx', function(d) {
                return 30;
            })
            .attr('r', 5);

        function relax() {
            var spacing = 18;
            var dy = 1;
            var repeat = false;
            labels = svg.selectAll('.label');
            labels.each(function(d1, i) {
                var a = this;
                var labelA = d3.select(a);
                var yA = labelA.attr('y');
                labels.each(function(d2, j) {
                    var b = this;
                    var labelB = d3.select(b);
                    var yB = labelB.attr('y');
                    if (a === b) {
                        return;
                    }
                    diff = yA - yB;
                    if (Math.abs(diff) > spacing) {
                        return;
                    }
                    repeat = true;
                    magnitude = diff > 0 ? 1 : -1;
                    adjust = magnitude * dy;
                    labelA.attr('y', +yA + adjust);
                    labelB.attr('y', +yB - adjust);
                    d1.y = +yA + adjust;
                    d2.y = +yB - adjust;
                })
            })
            if (repeat) {
                relax();
            }
        }

        var labels = svg.selectAll('.label')
            .data(question_data)
            .enter()
            .append('text')
            .attr('class', 'label')
            .attr('text-anchor', 'start')
            .attr('y', function(d) {
                return yScale(d.value) + 6;
            })
            .attr('x', function(d) {
                return label_margin_left;
            })
            .text(function(d) {
                return (d.lecturer);
            });

        relax();

        var polylines = svg.selectAll(".lines")
            .data(question_data);

        polylines.enter()
            .append("polyline")
            .attr("points", function(d) {
                var start = [
                    37, yScale(d.value)
                ];
                var midpoint = [
                    (37 + ((label_margin_left - 37) / 2)), yScale(d.value)
                ];
                end_y = yScale(d.value) === d.y ? d.y : (d.y - 6);
                var end = [
                    label_margin_left - 2, end_y
                ];
                return [start, midpoint, end];
            });
    });
})();
