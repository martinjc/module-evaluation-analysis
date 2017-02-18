var fs = require('fs');
var Nightmare = require('nightmare');
var nightmare = Nightmare({ show: false });

var args = process.argv.splice(2);
var template_file = args[0]

nightmare
    .goto(template_file)
    .pdf('test.pdf', {
        pageSize: 'A4',
        printBackground: true,
        landscape: true
    })
    .end()
    .then(function(){
        console.log('done');
    });
