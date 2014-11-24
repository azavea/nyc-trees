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
    sass = require('gulp-sass'),
    concat = require('gulp-concat'),
    postcss = require('gulp-postcss'),
    csswring = require('csswring'),
    gulpif = require('gulp-if'),
    livereload = require('gulp-livereload'),
    tmp = require('temporary'),
    del = require('del'),
    exec = require('child_process').exec,
    runSequence = require('run-sequence');

var args = minimist(process.argv.slice(2),
                    {default: {debug: false}}),

    entries = ['forgot_username.js'],
    entryFiles = entries.map(function(file) { return './js/src/' + file; }),
    intermediaryDir = new tmp.Dir().path + '/',
    bundleDir = intermediaryDir + 'js/',
    cssDir = intermediaryDir + 'css/',
    versionedDir = 'static/',
    buildTasks = ['browserify', 'sass', 'vendor-css'];

var collectstatic = function(cb) {
    exec('envdir /etc/nyc-trees.d/env /opt/app/manage.py collectstatic --noinput --clear', function(err) {
        gutil.log('Collected static');
        cb(err);
    });
};

gulp.task('version', buildTasks, function(cb) {
    gulp.src(intermediaryDir + '**')
         // Don't version source map files
        .pipe(revall({ ignore: [ /\.(js|css)\.map$/ ]}))
        .pipe(gulp.dest(versionedDir))
        .pipe(revall.manifest())
        .pipe(gulp.dest(versionedDir))
        .on('end', function() {
            collectstatic(cb);
        });
});

gulp.task('copy-assets', function(cb) {
    gulp.src(intermediaryDir + '**')
        .pipe(gulp.dest(versionedDir))
        .on('end', function() {
            collectstatic(cb);
        });
});

gulp.task('browserify', ['clean'], function() {
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
            return bundle
                .pipe(gulp.dest(bundleDir))
                .pipe(livereload({ auto: false }));
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
        .pipe(sass({outputStyle: 'compressed'}))
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest(cssDir))
        .pipe(livereload({ auto: false }));
});

gulp.task('vendor-css', ['clean'], function() {
    return gulp.src('css/**/*.css')
        .pipe(sourcemaps.init())
        .pipe(concat('vendor.css'))
        .pipe(gulpif(! args.debug, postcss([csswring])))
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest(cssDir));
});

gulp.task('clean', function(cb) {
    del([versionedDir + '*', '!' + versionedDir + '.gitignore'], cb);
});

gulp.task('default', ['version']);
gulp.task('build', function(cb) {
    runSequence(buildTasks, 'copy-assets', cb);
});

gulp.task('watch', ['watchify'], function() {
    // Note: JS rebuilding is handled by watchify, in order to utilize it's
    // caching behaviour
    livereload.listen();
    gulp.watch('sass/**/*.scss', ['sass']);
    // Rerun collectstatic whenever files are added to the static files dir
    gulp.watch(intermediaryDir + '**', ['copy-assets']);
});
