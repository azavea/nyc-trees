var $ = require('jquery');

var dataClass = function (t) { return '[data-class="group-detail-' + t + '"]'; };

var dom = {
    eventInfoContainer: dataClass('event-info'),
    eventInfoSubmenuToggle: dataClass('event-info-submenu-toggle'),
    eventInfoSubmenu: dataClass('event-info-submenu')
};

$(dom.eventInfoSubmenuToggle).on('click', function (e) {
    e.preventDefault();
    $(e.target).siblings(dom.eventInfoSubmenu).toggle();
});
