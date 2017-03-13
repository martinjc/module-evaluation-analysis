(function() {

    var module_data = d3.csvParse(d3.select('#data_agreement_overall')
        .html());
    var columns = module_data.columns.splice(1);

    module_data.forEach(function(d, i) {

        var chart = evaluationPie()
            .width(400)
            .height(250)
            .margin({
                top: 20,
                bottom: 40,
                left: 120,
                right: 120
            })
            .i(i)
            .columns(columns);

        var container = d3.select("#pie_vis" + i)
            .datum(d)
            .call(chart);

        container.select('h3')
            .html(d.question.replace(': ', ''));

    });

})();
