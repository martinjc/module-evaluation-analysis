var fs = require('fs');
var Nightmare = require('nightmare');
var nightmare = Nightmare({
    show: false
});

var args = process.argv.splice(2);
var template_file = args[0];
var output_file = args[1];

nightmare
    .goto(template_file)
    .pdf(output_file, {
        pageSize: 'A4',
        printBackground: true,
        landscape: false
    })
    .end()
    .then(function() {});
