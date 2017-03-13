(function() {

    var average_data = d3.csvParse(d3.select('#data_average')
        .html());

    var module_data = d3.csvParse(d3.select('#data_agreement_overall')
        .html());

    var comparison_data = module_data.map(function(d, i) {
        if (average_data[i].question === d.question) {
            return {
                'question': d.question.replace(': ', ''),
                'module': +d.Agree,
                'average': +average_data[i].Agree,
                'diff': (+d.Agree) - (+average_data[i].Agree)
            }
        }
    });

    var chart = againstAverage()
        .width(1100)
        .height(300)
        .margin({
            top: 40,
            bottom: 20,
            left: 60,
            right: 200,
        })

    var container = d3.select("#comparison")
        .datum(comparison_data)
        .call(chart);

})();
