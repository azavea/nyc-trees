"use strict";

var mapModule = require('./map');

var reservationsMap = mapModule.create({ static: true });

mapModule.addTileLayer(reservationsMap);