var gulp = require('gulp'),
    source = require('vinyl-source-stream'),
    browserify = require('browserify'),
    factor = require('factor-bundle'),
    fs = require('fs'),
    through = require('through2'),
    merge = require('merge-stream'),
    buffer = require('vinyl-buffer'),
    uglify = require('gulp-uglify'),
    sourcemaps = require('gulp-sourcemaps'),
    minimist = require('minimist'),
    watchify = require('watchify'),
    gutil = require('gulp-util'),
    revall = require('gulp-rev-all');

var args = minimist(process.argv.slice(2),
                    {default: {debug: false}}),

    entries = ['home.js', 'user.js'],
    entryFiles = entries.map(function(file) { return './js/' + file; }),
    intermediaryDir = './assets/',
    bundleDir = intermediaryDir + 'js/',
    versionedDir = 'static/';

gulp.task('version', ['browserify'], function() {
    return gulp.src(intermediaryDir + '**')
         // Don't version source map files
        .pipe(revall({ ignore: [ /\.js\.map$/ ]}))
        .pipe(gulp.dest(versionedDir))
        .pipe(revall.manifest())
        .pipe(gulp.dest(versionedDir));
});

gulp.task('browserify', function() {
    return browserifyTask(browserify({
        entries: entryFiles,
        debug: true
    }));
});

gulp.task('watchify', function() {
    var bundler = watchify(browserify({
        entries: entryFiles,
        debug: true,
        // Watchify requires these
        cache: {},
        packageCache: {},
        fullPaths: true
    }));

    bundler.on('update', function() {
        gutil.log("Rebundling JS");
        return browserifyTask(bundler);
    });

    return browserifyTask(bundler);
});

function browserifyTask(bundler) {
    // We need to use a through-stream for entry bundles so we can minify them
    var bundleStreams = entries.map(function() { return through(); });

    var commonBundle = bundler
        .plugin(factor, {
            entries: entryFiles,
            o: bundleStreams
        })
        .bundle()
        .on('error', gutil.log.bind(gutil, 'Browserify Error'))
        .pipe(source('common.js'));

    var entryBundles = bundleStreams.map(function(stream, i) {
        return bundleStreams[i].pipe(source(entries[i]));
    });

    var bundles = entryBundles.concat(commonBundle);

    bundles = bundles.map(function(bundle) {
        if (args.debug) {
            return bundle.pipe(gulp.dest(bundleDir));
        }
        return bundle
            .pipe(buffer())
            .pipe(sourcemaps.init({loadMaps: true}))
            .pipe(uglify())
            .pipe(sourcemaps.write('./'))
            .pipe(gulp.dest(bundleDir));
    });

    return merge.apply(this, bundles);
}

gulp.task('default', ['version']);
gulp.task('watch', ['watchify']);
