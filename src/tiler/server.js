"use strict";

var Windshaft = require('windshaft'),

    workerCount = process.env.WORKERS || require('os').cpus().length,
    port = process.env.PORT || 4000,

    dbUser = process.env.NYC_TREES_DB_USER || 'nyc_trees',
    dbPassword = process.env.NYC_TREES_DB_PASSWORD || 'nyc_trees',
    dbHost = process.env.NYC_TREES_DB_HOST || 'localhost',
    dbPort = process.env.NYC_TREES_DB_PORT || 5432,

    redisHost = process.env.NYC_TREES_REDIS_HOST || 'localhost',
    redisPort = process.env.NYC_TREES_REDIS_PORT || 6379,

    statsdHost = process.env.NYC_TREES_STATSD_HOST || 'localhost',
    statsdPort = process.env.NYC_TREES_STATSD_PORT || 8125,

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
            if (req.params.type == 'progress') {
                req.params.table = 'survey_blockface';
                req.params.interactivity = ['id'];

                req.params.sql = "(SELECT geom, id FROM survey_blockface) AS query";
                req.params.style = "#survey_blockface { line-color: #000000; line-opacity: 1; line-width: 2; }";
            } else {
                callback("Unrecognized request type", null);
            }

            callback(null, req);
        }
    };

Windshaft.Server(config).listen(port);

console.log("Now serving tiles");
