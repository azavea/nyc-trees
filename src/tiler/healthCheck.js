"use strict";

// Loading dependencies from a dependency is not a best practice, but
// I think it makes sense in this situation.  We want our health
// endpoint to check connectivity to postgres and redis in a way that
// matches real-world usage as closely as possible. Ideally this
// health check would be part of windshaft, so I am pulling in
// windshaft's installed versions of pg and redis.
var pg = require('windshaft/node_modules/pg');
var redis = require('windshaft/node_modules/redis-mpool/node_modules/redis');

function checkPostgres(host, port, user, password, database, timeout, cb) {
    var conString = ['postgres://', user, ':', password, '@', host, '/', database].join('');
    var client = new pg.Client(conString);
    var gotResponse = false;
    client.connect(function(err) {
        client.end();
        gotResponse = true;
        if (err) {
            cb({database: {error: err}});
        } else {
            cb({database: {ok: true}});
        }
    });

    setTimeout(function() {
        if (!gotResponse) {
            cb({database: {error: 'Timeout'}});
        }
    }, timeout);
}

function checkRedis(host, port, timeout, cb) {
    // I am skipping over connection pooling because we are most interested in
    // a basic connectivity check.
    var client = redis.createClient(port, host);
    var gotResponse = false;

    client.on('connect', function() {
        gotResponse = true;
        cb({cache: {ok: true}});
    });

    client.on('error', function() {
        // no arguments are passed when the error event is triggered
        // TODO: Find out how to return more useful failure information
        gotResponse = true;
        cb({
            cache: {
                error: {
                    message: ['Redis client raised an error event while connecting to ',
                              host, ':', port].join('')
                }
            }
        });
    });

    setTimeout(function() {
        if (!gotResponse) {
            cb({cache: {error: 'Timeout'}});
        }
    }, timeout);
}

function statusObjectFromException(ex) {
    return {
        error: {
            message: 'Exception in health check.',
            exception: ex && ex.toString ? ex.toString() : ex
        }
    };
}

module.exports = function createHealthCheckHandler(config, timeout) {
    // config should be the same config object passed to Windshaft.Server()
    var pgConf = config.grainstore.datasource,

        pgHost = pgConf.host,
        pgPort = pgConf.port,
        pgUser = pgConf.user,
        pgPassword = pgConf.password,
        pgDatabase = pgConf.user, // We require db name match username

        redisHost = config.redis.host,
        redisPort = config.redis.port;

    return function(req, res) {
        var status = {};

        try {
            checkPostgres(pgHost, pgPort, pgUser, pgPassword, pgDatabase, timeout,
                function(result) {
                    status.database = result.database;
                    if (status.cache) {
                        res.json(status);
                    }
                });
        } catch(e) {
            status.database = statusObjectFromException(e);
            if (status.cache) {
                res.json(status);
            }
        }

        try {
            checkRedis(redisHost, redisPort, timeout, function(result) {
                status.cache = result.cache;
                if (status.database) {
                    res.json(status);
                }
            });
        } catch(e) {
            status.cache = statusObjectFromException(e);
            if (status.database) {
                res.json(status);
            }
        }
   };
};
