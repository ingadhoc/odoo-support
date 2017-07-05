odoo.define('web_support_client.menu_links', function(require) {
"use strict";
var UserMenu = require('web.UserMenu');
var Model = require('web.Model');
var session = require('web.session');


UserMenu.include({
        on_menu_service_portal: function() {
            new Model("res.users")
                .call("get_signup_url")
                .then(function (url) {
                    window.open(url, '_blank');
                });
            // window.open('https://www.adhoc.com.ar/doc/how-to', '_blank');
        },
        on_menu_help_and_doc: function() {
            var P = new Model('ir.config_parameter');
            P.call('get_param', ['database.uuid']).then(function(dbuuid) {
                window.open('https://www.adhoc.com.ar/doc/624/624/' + dbuuid + '/' + session.uid, '_blank');
            });            
        },
    });
});
