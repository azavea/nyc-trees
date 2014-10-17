var gulp = require('gulp'),
    source = require('vinyl-source-stream'),
    browserify = require('browserify'),
    factor = require('factor-bundle'),
    fs = require('fs'),
    through = require('through2'),
    merge = require('merge-stream'),
    buffer = require('vinyl-buffer'),
    uglify = require('gulp-uglify'),
    sourcemaps = require('gulp-sourcemaps');

var entries = ['home.js', 'user.js'],
    entryFiles = entries.map(function(file) { return './js/' + file; }),
    bundleDir = 'bundle/';

gulp.task('browserify', function() {
    // We need to use a through-stream for entry bundles so we can minify them
    var bundleStreams = entries.map(function() { return through(); });

    var commonBundle = browserify({
        entries: entryFiles,
        debug: true
    })
    .plugin(factor, {
        entries: entryFiles,
        o: bundleStreams
    })
    .bundle()
    .pipe(source('common.js'));

    var entryBundles = bundleStreams.map(function(stream, i) {
        return bundleStreams[i].pipe(source(entries[i]));
    });

    var bundles = entryBundles.concat(commonBundle);

    bundles = bundles.map(function(bundle) {
        return bundle
            .pipe(buffer())
            .pipe(sourcemaps.init({loadMaps: true}))
            .pipe(uglify())
            .pipe(sourcemaps.write('./'))
            .pipe(gulp.dest(bundleDir));
    });

    return merge.apply(this, bundles);
});

gulp.task('default', ['browserify']);
