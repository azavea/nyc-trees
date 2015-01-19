"use strict";

var Windshaft = require('windshaft'),
    fs = require('fs'),
    _ = require('lodash'),
    files = require('./files'),
    port = process.env.PORT || 4000,

    dbUser = process.env.NYC_TREES_DB_USER || 'nyc_trees',
    dbPassword = process.env.NYC_TREES_DB_PASSWORD || 'nyc_trees',
    dbHost = process.env.NYC_TREES_DB_HOST || 'localhost',
    dbPort = process.env.NYC_TREES_DB_PORT || 5432,

    redisHost = process.env.NYC_TREES_REDIS_HOST || 'localhost',
    redisPort = process.env.NYC_TREES_REDIS_PORT || 6379,

    statsdHost = process.env.NYC_TREES_STATSD_HOST || 'localhost',
    statsdPort = process.env.NYC_TREES_STATSD_PORT || 8125,

    queries = files('./sql'),
    styles = files('./style'),

    interactivity = {
        progress: 'id,group_id,survey_type'
    },

    config = {
        base_url: '/:cache_buster/:dbname/:type',
        base_url_notable: '/:cache_buster/:dbname',

        grainstore: {
            datasource: {
                user: dbUser,
                password: dbPassword,
                host: dbHost,
                port: dbPort,
                geometry_field: 'geom',
                srid: 4326
            }
        },
        redis: {
            host: redisHost,
            port: redisPort
        },

        statsd: {
            host: statsdHost,
            port: statsdPort
        },

        enable_cors: true,

        req2params: function(req, callback) {
            try {
                // Windshaft needs a table name, even if you are providing
                // a custom sql statement.
                req.params.table = 'survey_blockface';
                req.params.sql = req2sql(req);
                req.params.style = req2style(req);
                req.params.interactivity = req2interactivity(req);
                callback(null, req);
            } catch(err) {
                callback(err, null);
                return;
            }
        }
    };

function req2context(req) {
    // constructs a context object that will be passed to
    // SQL and CartoCSS templates.
    var context = {},
        user_id;
    if (req.query.user) {
        user_id = parseInt(req.query.user, 10);
        if (isNaN(user_id)) {
            throw 'Could not parse "user" query string argument ' +
                '(' + req.query.user + ') as an integer';
        }
        context.user_id = user_id;
    }
    return context;
}

function req2interactivity(req) {
    return interactivity[req.params.type];
}

function req2style(req) {
    // At the time this was written we have a single stylesheet
    // for all requests
    return styles.progress();
}

function req2sql(req) {
    /*
     This function expects the SQL files loaded into the
     'queries' object to have a specific naming convention. If
     a user= query string argument is provided, this funciton
     prepends 'user_' to the 'type' parameter to generate the
     SQL file name. Example:

     URL:  /123456/nyc_trees/foo/1/2/3.png
     File: foo.sql

     URL:  /123456/nyc_trees/foo/1/2/3.png?user=1
     File: user_foo.sql

     */
    var queryPrefix = req.query.user ? 'user_' : '',
        queryName = queryPrefix + req.params.type,
        context = req2context(req),
        additionalErr = '';
    if (queries[queryName]) {
        return queries[queryName](context);
    } else {
        if (queries['user_' + queryName]) {
            additionalErr = 'There is a query defined for user_' + queryName +
                '. Did you forget the user= query string argument?';
        }
        throw 'No query defined for ' + queryName + '. ' + additionalErr;
    }
}

Windshaft.Server(config).listen(port);
console.log("Now serving tiles");
