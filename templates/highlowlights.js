(function(){

    var highlights_table = d3.select('.highlights table tbody');
    var lowlights_table = d3.select('.lowlights table tbody');

    var colourScale = d3.scaleLinear()
        .domain([0,0.7,1])
        .range(["hsla(0, 60%, 50%, 1)", "hsla(45, 70%, 60%, 1)", "hsla(90, 50%, 50%, 1)"]);

    var pformat = d3.format('.1%');

    var module_data = d3.csvParse(d3.select('#data_agreement_comparison').html(), function(d){
        return {
            question: d.question,
            module: +d.module,
            AllModules: +d.AllModules
        }
    });

    module_data = module_data.filter(function(d){
        return d.question !== "Overall, I am satisfied with the quality of this module.";
    })

    module_data.sort(function(a, b){
        return b.module - a.module;
    })

    var lowlights = module_data.slice(module_data.length-3, module_data.length);
    var highlights = module_data.slice(0, 3);

    highlights_table.selectAll('tr')
        .data(highlights)
        .enter()
        .append('tr')
        .style('color', function(d){
            return colourScale(d.module);
        })
        .html(function(d){
            return '<td>' + d.question + '</td><td>' + pformat(d.module) + '</td><td style="color: ' + colourScale(d.AllModules) + ';">' + pformat(d.AllModules) + '</td>'
        });

    lowlights_table.selectAll('tr')
        .data(lowlights)
        .enter()
        .append('tr')
        .style('color', function(d){
            return colourScale(d.module);
        })
        .html(function(d){
            return '<td>' + d.question + '</td><td>' + pformat(d.module) + '</td><td>' + pformat(d.AllModules) + '</td>'
        });


})();
