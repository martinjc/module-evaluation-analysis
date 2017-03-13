(function() {

    var module_data = d3.csvParse(d3.select('#data_agreement_comparison')
        .html());

    module_data.forEach(function(d) {
        d.question = d.question.replace(': ', ''),
            d.module = +d.module;
        d.average = +d.AllModules;
        d.diff = (+d.module) - +(d.AllModules);
    })

    var chart = againstAverage()
        .width(1100)
        .height(600)
        .margin({
            top: 40,
            bottom: 20,
            left: 60,
            right: 400,
        })

    var container = d3.select("#agreement_evaluation_vis")
        .datum(module_data)
        .call(chart);

})();
