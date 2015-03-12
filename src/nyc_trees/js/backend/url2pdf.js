// Based on https://github.com/ariya/phantomjs/blob/master/examples/rasterize.js

var page = require('webpage').create(),
    system = require('system');

if (system.args.length !== 3) {
    console.log('Usage: url2pdf.js url zoomFactor');
    phantom.exit(1);
}

var url = system.args[1],
    zoomFactor = system.args[2];

// The PhantomJS documentation doesn't explain the relationship between
// viewportSize and paperSize for PDF output. One would imagine that
// the page is rendered to a bitmap whose size is the viewportSize,
// and the bitmap is then rendered to the PDF at some DPI resolution.
// It doesn't appear to be that simple, at least when rendering Leaflet maps.
// However, using 96 DPI gives a reasonable result.

var DPI = 96;
page.viewportSize = {
    width: 7.5 * DPI,  // 8.5in with .5in margins
    height: 10 * DPI   //  11in with .5in margins
};
page.paperSize = {
    format: 'letter',
    orientation: 'portrait',
    margin: '0.5in'
};
page.zoomFactor = zoomFactor;

page.open(url, function (status) {
    if (status !== 'success') {
        console.log('Unable to load given URL.');
        phantom.exit(2);
    } else {
        window.setTimeout(function () {
            page.render('/dev/stdout', { format: 'pdf' });
            phantom.exit();
        }, 200);
    }
});
