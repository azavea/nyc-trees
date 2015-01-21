"use strict";

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
    revall = require('gulp-rev-all'),
    sass = require('gulp-ruby-sass'),
    concat = require('gulp-concat'),
    postcss = require('gulp-postcss'),
    csswring = require('csswring'),
    gulpif = require('gulp-if'),
    livereload = require('gulp-livereload'),
    tmp = require('temporary'),
    del = require('del'),
    shell = require('gulp-shell'),
    runSequence = require('run-sequence'),
    jshint = require('gulp-jshint');

var args = minimist(process.argv.slice(2),
                    {default: {debug: false}}),

    entries = [
        'activation_form.js',
        'base.js',
        'datetimepicker_polyfill.js',
        'event.js',
        'eventCheckin.js',
        'event_form.js',
        'event_list_page.js',
        'group_detail.js',
        'group_list.js',
        'group_settings.js',
        'progressPage.js',
        'registrationBase.js',
        'reservationPage.js',
        'reserveBlockfacePage.js',
        'userProfile.js',
        'userSettings.js',
    ],
    entryFiles = entries.map(function(file) { return './js/src/' + file; }),

    vendorCssFiles = [
        'css/**/*.css',
        'node_modules/leaflet/dist/leaflet.css'
    ],

    intermediaryDir = new tmp.Dir().path + '/',
    bundleDir = intermediaryDir + 'js/',
    cssDir = intermediaryDir + 'css/',
    versionedDir = '/var/cache/nyc-trees/static/',

    buildTasks = [
        'browserify',
        'browserify-tests',
        'sass',
        'vendor-css',
        'copy'
    ],
    collectstatic = 'envdir /etc/nyc-trees.d/env /opt/app/manage.py collectstatic --noinput';


gulp.task('collect-prod', ['version'], shell.task(collectstatic));
gulp.task('collect-debug', ['copy-dev-assets'], shell.task(collectstatic));

gulp.task('version', buildTasks, function(cb) {
    return gulp.src(intermediaryDir + '**')
         // Don't version source map files
        .pipe(revall({
            ignore: [
                // Ignore source maps.
                /\.(js|css)\.map$/,
                // Ignore test bundle.
                /test\.bundle\.js$/
            ]
        }))
        .pipe(gulp.dest(versionedDir, {mode: '0775'}))
        .pipe(revall.manifest())
        .pipe(gulp.dest(versionedDir, {mode: '0775'}));
});

// Images and fonts need to be copied in order to be versioned and collected
gulp.task('copy', ['copy-fonts', 'copy-images']);

gulp.task('copy-fonts', function() {
    return gulp.src(['font/**'])
        .pipe(gulp.dest(intermediaryDir + 'font/'));
});

gulp.task('copy-images', function() {
    return gulp.src(['img/**'])
        .pipe(gulp.dest(intermediaryDir + 'img/'));
});

gulp.task('copy-dev-assets', function(cb) {
    return gulp.src(intermediaryDir + '**')
        .pipe(gulp.dest(versionedDir, {mode: '0775'}));
});

gulp.task('browserify', ['clean'], function() {
    return browserifyTask(browserify({
        entries: entryFiles,
        debug: true
    }));
});

gulp.task('browserify-tests', ['clean'], function() {
    gutil.log("Rebundling test bundle JS");
    return browserify({
            entries: ['./js/test/tests.js'],
            debug: true
        })
        .bundle()
        .pipe(source('test.bundle.js'))
        .pipe(gulp.dest(bundleDir));
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
    var entryBundles = entries.map(function(_, i) {
        return through().pipe(source(entries[i]));
    });

    var commonBundle = bundler
        .plugin(factor, {
            entries: entryFiles,
            outputs: entryBundles
        })
        .bundle()
        .on('error', gutil.log.bind(gutil, 'Browserify Error'))
        .on('error', process.exit.bind(process, 1))
        .pipe(source('common.js'));

    var bundles = entryBundles.concat(commonBundle);

    bundles = bundles.map(function(bundle) {
        if (args.debug) {
            return bundle
                .pipe(gulp.dest(bundleDir));
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

gulp.task('sass', ['clean'], function() {
    return gulp.src('sass/main.scss')
        .pipe(sourcemaps.init())
        .pipe(sass({style: 'compressed'}))
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest(cssDir));
});

gulp.task('vendor-css', ['clean'], function() {
    return gulp.src(vendorCssFiles)
        .pipe(sourcemaps.init())
        .pipe(concat('vendor.css'))
        .pipe(gulpif(! args.debug, postcss([csswring])))
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest(cssDir));
});

gulp.task('clean', function(cb) {
    del([versionedDir + '*'], {force: true}, cb);
});

gulp.task('default', ['collect-prod']);
gulp.task('build', function(cb) {
    runSequence(buildTasks, 'collect-debug', cb);
});

gulp.task('watch', ['watchify'], function() {
    // Note: JS rebuilding is handled by watchify, in order to utilize it's
    // caching behaviour
    livereload.listen({auto: true });
    gulp.watch('sass/**/*.scss', ['sass']);
    // Rerun collectstatic whenever files are added to the static files dir
    gulp.watch(intermediaryDir + '**', ['collect-debug']);
});

gulp.task('watch-tests', function() {
    function bundleTests() {
        runSequence('lint', 'browserify-tests');
    }
    gulp.watch('js/**/*.js', bundleTests);
    gulp.watch(intermediaryDir + '**', ['collect-debug']);
});

gulp.task('lint', function() {
    return gulp.src(['./js/src/**/*.js', './js/test/**/*.js'])
        .pipe(jshint())
        .pipe(jshint.reporter('default'))
        .pipe(jshint.reporter('fail'));
});
