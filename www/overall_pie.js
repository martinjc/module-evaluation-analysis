(function(){

    var width = 600;
    var height = 500;

    var margin = {
        top: 20,
        bottom: 20,
        left: 100,
        right: 250,
    };

    var pformat = d3.format('.1%');

    var svg = d3.select("#overall_pie_vis")
        .append("svg")
            .attr("width", width)
            .attr("height", height)
        .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

    width = width - margin.left - margin.right;
    height = height - margin.top - margin.bottom;

    var module_data = d3.csvParse(d3.select('#data_module').html());

    var column = 'Overall, I am satisfied with the quality of this module.'

    this_data = []
    module_data.forEach(function(d){
        if(d.question === column) {
            this_data = d;
        }
    });

    columns = module_data.columns.splice(1);

    pie_data = [];
    columns.forEach(function(c){
        if(+this_data[c] > 0) {
            pie_data.push({key: c, value: +this_data[c]})
        }
    });

    svg = svg
        .append("g")
            .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

    svg.append("g")
        .attr("class", "slices")

    svg.append("g")
        .attr("class", "labels")

    svg.append("g")
        .attr("class", "lines")

    var radius = Math.min(width, height)/2;

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

    function wrap(text, width) {
        text.each(function() {
            var text = d3.select(this);
            var words = text.text().split(/\s+/).reverse();
            var word;
            var line = [];
            var lineNumber = 0;
            var lineHeight = 0.5;
            var y = text.attr("y");
            var x = 0;
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
                        .attr("dx", dx + "em")
                        .text(word);
                }
            }
        });
    }

    var pie = d3.pie()
        .sort(null)
        .value(function(d) { return d.value; });

    var key = function(d){ return d.data.key; }

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
          .style("fill", function(d) { return colourScale(d.data.key); });

    var text = svg.select(".labels")
            .selectAll("text")
            .data(pie(pie_data), key);

    function midAngle(d) {
        return d.startAngle + (d.endAngle - d.startAngle)/2;
    }

    text
        .enter()
          .append("text")
          .attr("transform", function(d) {
              var pos = labelArc.centroid(d);
              pos[0] = radius * (midAngle(d) < Math.PI ? 1 : -1);
              return "translate(" + pos + ")";
          })
          .style("text-anchor", function(d){
              return midAngle(d) < Math.PI ? "start":"end";
          })
          .attr("dy", ".35em")
          .attr("dx", ".35em")
          .attr("fill", "#111")
          .text(function(d) { return d.data.key + " (" + pformat(d.data.value) + ")"; })
          .call(wrap, margin.right);

    var polyline = svg.select(".lines")
                .selectAll("polyline")
                .data(pie(pie_data), key);

    polyline.enter()
        .append("polyline")
        .attr("points", function(d){
            var pos = labelArc.centroid(d);
            pos[0] = radius * 0.95 * (midAngle(d) < Math.PI ? 1 : -1);
            return [arc.centroid(d), labelArc.centroid(d), pos];
        });
})();
