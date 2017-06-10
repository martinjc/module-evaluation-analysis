function highlowTable() {

    var colourScale = d3.scaleLinear()
        .domain([0, 0.7, 1])
        .range(["hsla(0, 60%, 50%, 1)", "hsla(45, 70%, 60%, 1)", "hsla(90, 50%, 50%, 1)"]);

    var pformat = d3.format('.1%');

    function table(selection) {
        selection.each(function(data) {
            table = d3.select(this);
            data.forEach(function(d) {
                table.append('tr')
                    .style('color', colourScale(d.Agree))
                    .html('<td>' + d.question + '</td><td>' + pformat(d.Agree) + '</td><td style="color: ' + colourScale(d.average) + ';">' + pformat(d.average) + '</td>')
            });

        });
    }

    return table;
};
