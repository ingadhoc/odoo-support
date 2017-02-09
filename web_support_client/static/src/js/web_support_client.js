(function(){
    "use strict";
    openerp.web.UserMenu.include({
        // TODO make this urls paramers
        on_menu_service_portal: function() {
            new openerp.web.Model("res.users")
                .call("get_signup_url")
                .then(function (url) {
                    window.open(url, '_blank');
                });
            // window.open('https://www.adhoc.com.ar/web/', '_blank');
        },
        on_menu_help_and_doc: function() {
            window.open('https://www.adhoc.com.ar/doc/how-to', '_blank');
        },
    });
})();