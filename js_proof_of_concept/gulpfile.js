var gulp = require('gulp'),
    source = require('vinyl-source-stream'),
    browserify = require('browserify'),
    factor = require('factor-bundle'),
    fs = require('fs'),
    path = require('path');

var entries = ['home.js', 'user.js'],
    entryFiles = entries.map(function(file) { return './js/' + file; }),
    bundleDir = 'bundle/',
    entryBundles = entries.map(function(file) { return path.resolve(bundleDir + file); });

gulp.task('browserify', function() {
    console.log(entryFiles);
    console.log(entryBundles);
    return browserify({
        entries: entryFiles
    })
    .plugin(factor, {
        entries: entryFiles,
        o: entryBundles
    })
    .bundle()
    .pipe(source('common.js'))
    .pipe(gulp.dest(bundleDir));
});

gulp.task('default', ['browserify']);
