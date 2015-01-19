"use strict";

/*

Read a directory of files and return an object where the key is the
file name without the file extension and the value is a function that
takes a template context object and returns the string content of the
file after template replacement. If the SQL file does not contain any
template tags, the function simply returns the static string, ignoring
the context object argument.

Example
-------

$ ls ./sql
.
..
bar.sql
foo.sql
user_foo.sql

$ node
> var queries = require('./queries')('./sql');
undefined
> queries.bar
[Function]

*/

var _ = require('lodash'),
    fs = require('fs'),
    path = require('path');

module.exports = function(dirName) {
    return _(dirToFilesObj(dirName))
        .mapValues(utf8FileToContentFunction)
        .value();
};

function dirToFilesObj(dirName) {
     return _(fs.readdirSync(dirName))
        .filter(isRealFile)
        .reduce(_.partial(objAddFileReference, dirName), {});}

function objAddFileReference(dirName, obj, fileName) {
    obj[stripExtension(fileName)] = path.join(dirName, fileName);
    return obj;
}

function isRealFile(filePath) {
    return (filePath !== '.' && filePath !== '..');
}

function stripExtension(filename) {
    return filename.replace(/\.[^/.]+$/, "");
}

function isTemplate(str) {
    return !!str.match(/<%=/);
}

function utf8FileToContentFunction(filePath) {
    return contentToFunction(
        fs.readFileSync(filePath, {encoding: 'utf8'})
    );
}

function contentToFunction(content) {
    if (isTemplate(content)) {
        return _.template(content);
    } else {
        return function() {
            return content;
        };
    }
}
