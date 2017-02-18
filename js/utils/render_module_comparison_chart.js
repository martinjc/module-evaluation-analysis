const jsdom = require('jsdom');

var htmlstub = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Template</title></head><body><div id="vis"></div></body></html>';
jsdom.env({
    html: htmlstub,
    scripts: ["vendor/d3.min.js"],
    done: function(err, window) {
        var d3 = window.d3;
        var svg = d3.select('#vis')
            .append('svg')
            .attr('width', '500')
            .attr('height', '500')
            .attr('xmlns', "http://www.w3.org/2000/svg");

        svg.append('circle')
            .attr('cx', 300)
            .attr('cy', 200)
            .attr('r', 100)
            .attr('fill', 'black');

        var pagesrc = window.document.documentElement.innerHTML;
        console.log(pagesrc);
        fs.writeFile(data_dir + 'templates/image-complete.html', pagesrc, function(err){
            if(err) {
                console.log('nope');
            } else {
                console.log('claiming its written');
                var phps = spawn(data_dir + 'phantomjs/bin/phantomjs', [data_dir + 'utils/read-and-render-template.js', data_dir + 'templates/image-complete.html', data_dir + 'img/image']);
                phps.on('close', function(){
                    console.log('phantom ended');
                    fs.readFile(data_dir + 'img/image-1024x768.png', function(err, data){
                        res.setHeader('Content-Type', contentTypes['png']);
                        res.end(data);
                    });
                })
            }
        })
        var svgsrc = d3.select('#vis').html();
        fs.writeFile(data_dir + 'img/img.svg', svgsrc, function(err){
            if(err) {
                console.log('nope2');
            }
        })
    }
});
