var fs = require('fs');
var system = require('system');
var page = require('webpage').create();

var args = system.args.splice(1);
console.log(args)

var template = args[0];
console.log(template);

var scriptfile = args[1];
console.log(scriptfile);

var output = args[2];
console.log(output);

var html_string = fs.read(template);
var js_string = fs.read(scriptfile);

page.content = html_string;
page.includeJs(
    'https://d3js.org/d3.v4.js', function(){
        //page.injectJs('utils/render_module_comparison_chart.js');
        page.evaluateJavaScript(js_string);
    }
)



page.render('test.png');
