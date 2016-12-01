odoo.define('web_support_client_issue.support_new_issue_wizzard', function (require) {
"use strict";
    var UserMenu = require('web.UserMenu');
    UserMenu.include({
        on_menu_new_issue: function() {
            var self = this;
            self.rpc("/web/action/load", { action_id: "web_support_client_issue.action_support_new_issue_wizzard" }).then(function(result) {
                // con esto setea el res del actual user pero nos queremos uno nuevo
                // result.res_id = instance.session.uid;
                return self.do_action(result);
            });
        },
    });
});
