(function(){

    var width = 600;
    var height = 400;

    var margin = {
        top: 20,
        bottom: 20,
        left: 100,
        right: 200,
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
            var lineHeight = 1;
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
                        .attr("dy", lineHeight + "em")
                        .attr("dx", dx + "em")
                        .text(word);
                }
            }
        });
    }

    function getTransformation(transform) {
      var g = document.createElementNS("http://www.w3.org/2000/svg", "g");

      g.setAttributeNS(null, "transform", transform);
      var matrix = g.transform.baseVal.consolidate().matrix;

      // Below calculations are taken and adapted from the private function
      // transform/decompose.js of D3's module d3-interpolate.
      var {a, b, c, d, e, f} = matrix;
      var scaleX, scaleY, skewX;
      if (scaleX = Math.sqrt(a * a + b * b)) a /= scaleX, b /= scaleX;
      if (skewX = a * c + b * d) c -= a * skewX, d -= b * skewX;
      if (scaleY = Math.sqrt(c * c + d * d)) c /= scaleY, d /= scaleY, skewX /= scaleY;
      if (a * d < b * c) a = -a, b = -b, skewX = -skewX, scaleX = -scaleX;
      return {
        translateX: e,
        translateY: f,
        rotate: Math.atan2(b, a) * Math.PI/180,
        skewX: Math.atan(skewX) * Math.PI/180,
        scaleX: scaleX,
        scaleY: scaleY
      };
    }

    function arrangeLabels() {
        var move = 1;
        while (move > 0) {
            move = 0;
            svg.selectAll(".label")
                .each(function() {
                    var that = this;
                    var a = this.getBoundingClientRect();
                    svg.selectAll(".label")
                        .each(function() {
                            if (this != that) {
                                var b = this.getBoundingClientRect();
                                if ((Math.abs(a.left - b.left) * 2 < (a.width + b.width)) && (Math.abs(a.top - b.top) * 2 < (a.height + b.height))) {
                                    var dx = (Math.max(0, a.right - b.left) + Math.min(0, a.left - b.right)) * 0.01;
                                    var dy = (Math.max(0, a.bottom - b.top) + Math.min(0, a.top - b.bottom)) * 0.02;
                                    var tt = getTransformation(d3.select(this).attr("transform"));
                                    var to = getTransformation(d3.select(that).attr("transform"));
                                    move += Math.abs(dx) + Math.abs(dy);

                                    to.translate = [to.translateX + dx, to.translateY + dy];
                                    tt.translate = [tt.translateX - dx, tt.translateY - dy];
                                    d3.select(this).attr("transform", "translate(" + tt.translate + ")");
                                    d3.select(that).attr("transform", "translate(" + to.translate + ")");
                                    a = this.getBoundingClientRect();
                                }
                            }
                        });
                });
        }
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
          .attr('class', 'label')
          .attr('id', function(d, i){
              return 'l-' + i;
          })
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
          .call(wrap, margin.right-50);

    arrangeLabels();

    var polyline = svg.select(".lines")
                .selectAll("polyline")
                .data(pie(pie_data), key);

    polyline.enter()
        .append("polyline")
        .attr("points", function(d, i){
            var label = d3.select('#l-' + i);
            var transform = getTransformation(label.attr("transform"));
            var pos = labelArc.centroid(d);
            pos[0] = transform.translateX;
            pos[1] = transform.translateY;
            var mid = labelArc.centroid(d);
            mid[1] = transform.translateY;
            return [arc.centroid(d), mid, pos];
        });
})();