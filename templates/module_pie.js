(function() {

    var width = 600;
    var height = 400;

    var module_data = d3.csvParse(d3.select('#data_module')
        .html());
    var column = 'Overall, I am satisfied with the quality of this module.'

    this_data = []
    module_data.forEach(function(d) {
        if (d.question === column) {
            this_data = d;
        }
    });

    columns = module_data.columns.splice(1);

    var chart = evaluationPie()
        .width(600)
        .height(400)
        .margin({
            top: 20,
            bottom: 20,
            left: 100,
            right: 200,
        })
        .columns(columns);

    var container = d3.select("#overall_pie_vis")
        .datum(this_data)
        .call(chart);
})();
