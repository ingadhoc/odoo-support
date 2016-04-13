(function(){
    "use strict";
    openerp.web.UserMenu.include({
        // TODO make this urls paramers
            on_menu_service_portal: function() {
            window.open('https://www.adhoc.com.ar/web/', '_blank');
            // TODO make this url came from contract data
            // window.open('doc/how-to', '_blank');
        },
            on_menu_help_and_doc: function() {
            window.open('https://www.adhoc.com.ar/doc/how-to', '_blank');
        },
    });
})();