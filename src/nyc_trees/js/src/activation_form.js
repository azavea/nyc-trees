"use strict";

var $ = require('jquery');

var dom = {
    chkRefererGroup: '#chk_referer_group',
    drpRefererGroup: '#referer_group'
};

$(dom.chkRefererGroup).click(function(e) {
    var checked = $(this).prop('checked');
    $(dom.drpRefererGroup).toggleClass('hidden', !checked);
});
