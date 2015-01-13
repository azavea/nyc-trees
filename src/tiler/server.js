"use strict";

var Windshaft = require('windshaft'),
    fs = require('fs'),
    _ = require('lodash'),

    port = process.env.PORT || 4000,

    dbUser = process.env.NYC_TREES_DB_USER || 'nyc_trees',
    dbPassword = process.env.NYC_TREES_DB_PASSWORD || 'nyc_trees',
    dbHost = process.env.NYC_TREES_DB_HOST || 'localhost',
    dbPort = process.env.NYC_TREES_DB_PORT || 5432,

    redisHost = process.env.NYC_TREES_REDIS_HOST || 'localhost',
    redisPort = process.env.NYC_TREES_REDIS_PORT || 6379,

    statsdHost = process.env.NYC_TREES_STATSD_HOST || 'localhost',
    statsdPort = process.env.NYC_TREES_STATSD_PORT || 8125,

    progressSql = fs.readFileSync('sql/progress.sql', {encoding: 'utf8'}),
    userProgressSql = _.template(fs.readFileSync('sql/user_progress.sql', {encoding: 'utf8'})),

    progressStyle = fs.readFileSync('style/progress.mss', {encoding: 'utf8'}),

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
            var user_id;

            try {
                if (req.params.type == 'progress') {
                    req.params.table = 'survey_blockface';
                    req.params.interactivity = 'id,group_id,survey_type';

                    req.params.style = progressStyle;

                    if ('user' in req.query) {
                        user_id = parseInt(req.query.user, 10);
                        req.params.sql = userProgressSql({user_id: user_id});
                    } else {
                        req.params.sql = progressSql;
                    }

                } else {
                    callback("Unrecognized request type", null);
                }
            } catch(err) {
                callback(err, null);
            }

            callback(null, req);
        }
    };

Windshaft.Server(config).listen(port);

console.log("Now serving tiles");
