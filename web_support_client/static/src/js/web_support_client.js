odoo.define('web_support_client.menu_links', function(require) {
"use strict";
var UserMenu = require('web.UserMenu');
var Model = require('web.Model');
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
            window.open('https://www.adhoc.com.ar/doc/624', '_blank');
        },
    });
});
