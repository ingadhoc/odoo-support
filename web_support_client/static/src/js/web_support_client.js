(function(){
    "use strict";
    openerp.web.UserMenu.include({
            on_menu_service_portal: function() {
            window.open('https://www.adhoc.com.ar/web/', '_blank');
            // TODO make this url came from contract data
            // window.open('doc/how-to', '_blank');
        },
    });
})();