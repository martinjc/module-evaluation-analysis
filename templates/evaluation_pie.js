function evaluationPie() {

    var width = 400;
    var height = 250;

    var margin = {
        top: 20,
        bottom: 40,
        left: 120,
        right: 120,
    };

    var columns = [];

    var radius = Math.min(width, height) / 2;

    var pformat = d3.format('.1%');

    var colourScale = d3.scaleOrdinal()
        .domain(['N/A', 'Disagree', 'Neither Agree nor Disagree', 'Agree'])
        .range(["#222", "hsla(0, 60%, 50%, 1)", "hsla(45, 70%, 60%, 1)", "hsla(90, 50%, 50%, 1)"]);

    var arc = d3.arc()
        .outerRadius(radius * 0.6)
        .innerRadius(radius * 0.1)
        .padAngle(.02)
        .padRadius(100)
        .cornerRadius(2);

    var labelArc = d3.arc()
        .outerRadius(radius)
        .innerRadius(radius);

    var pie = d3.pie()
        .sort(null)
        .value(function(d) {
            return d.value;
        });

    var key = function(d) {
        return d.data.key;
    }

    function pieChart(selection) {
        selection.each(function(data) {
            //draw the pie chart
            var svg = d3.select(this)
                .append("svg")
                .attr("width", width)
                .attr("height", height)
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

            width = width - margin.left - margin.right;
            height = height - margin.top - margin.bottom;

            svg = svg
                .append("g")
                .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

            svg.append("g")
                .attr("class", "slices");

            svg.append("g")
                .attr("class", "labels");

            svg.append("g")
                .attr("class", "lines");

            pie_data = [];
            columns.forEach(function(c) {
                if (+data[c] > 0) {
                    pie_data.push({
                        key: c,
                        value: +data[c]
                    });
                }
            });

            var slice = svg.select(".slices")
                .selectAll("path.slice")
                .data(pie(pie_data), key);

            slice
                .enter()
                .insert("path")
                .attr("d", arc)
                .attr("class", "slice")
                .style("stroke", "black")
                .style("stroke-width", "0.5px")
                .style("fill", function(d) {
                    return colourScale(d.data.key);
                });
        })
    }
}
