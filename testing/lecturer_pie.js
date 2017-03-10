(function() {

    var module_data = d3.csvParse(d3.select('#data_agreement_overall')
        .html());
    var columns = module_data.columns.splice(1);

    module_data.forEach(function(d, i) {

        var chart = evaluationPie()
            .width(500)
            .height(400)
            .margin({
                top: 50,
                bottom: 50,
                left: 120,
                right: 120,
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
