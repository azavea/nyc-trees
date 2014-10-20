# Local Development for JS/SASS

The main tool used is [gulp](http://gulpjs.com/), which is exposed through `npm run` to avoid version conflicts.

 - To create JS bundles, compile sass, and concatenate third-party css, minify CSS and JS, and version files using `gulp-rev-all`, use `gulp` or `npm run build`.
 - To do the above but skip minification and versioning, use `gulp build --debug` or `npm run build-debug`.
 - To watch files and automatically rebuild the JS or sass files when they change, use `gulp watch --debug` or `npm run watch`.  This will also start a livereload server.

`gulp build` and `gulp watch` without the `--debug` flag are intentionally not exposed through `npm run`.

**Note** The `watch` and `build` tasks do not do versioning of files, and thus files will end up in the `assets/` directory, not the `static/` directory.  This is intentional.
