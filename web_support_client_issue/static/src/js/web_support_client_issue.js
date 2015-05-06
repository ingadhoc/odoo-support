(function(){
    "use strict";
    openerp.web.UserMenu.include({
        on_menu_new_issue: function() {
            var self = this;
            if (!this.getParent().has_uncommitted_changes()) {
                self.rpc("/web/action/load", { action_id: "web_support_client_issue.action_support_new_issue_wizzard" }).done(function(result) {
                    // con esto setea el res del actual user pero nos queremos uno nuevo
                    // result.res_id = instance.session.uid;
                    self.getParent().action_manager.do_action(result);
                });
            }
        },
    });
})();

// Tres casos que nos van a servir:
//     on_menu_settings: function() {
//         var self = this;
//         if (!this.getParent().has_uncommitted_changes()) {
//             self.rpc("/web/action/load", { action_id: "base.action_res_users_my" }).done(function(result) {
//                 result.res_id = instance.session.uid;
//                 self.getParent().action_manager.do_action(result);
//             });
//         }
//     },
//     on_menu_account: function() {
//         var self = this;
//         if (!this.getParent().has_uncommitted_changes()) {
//             var P = new instance.web.Model('ir.config_parameter');
//             P.call('get_param', ['database.uuid']).then(function(dbuuid) {
//                 var state = {
//                             'd': instance.session.db,
//                             'u': window.location.protocol + '//' + window.location.host,
//                         };
//                 var params = {
//                     response_type: 'token',
//                     client_id: dbuuid || '',
//                     state: JSON.stringify(state),
//                     scope: 'userinfo',
//                 };
//                 instance.web.redirect('https://accounts.odoo.com/oauth2/auth?'+$.param(params));
//             }).fail(function(result, ev){
//                 ev.preventDefault();
//                 instance.web.redirect('https://accounts.odoo.com/web');
//             });
//         }
//     },
//     on_menu_about: function() {
//         var self = this;
//         self.rpc("/web/webclient/version_info", {}).done(function(res) {
//             var $help = $(QWeb.render("UserMenu.about", {version_info: res}));
//             $help.find('a.oe_activate_debug_mode').click(function (e) {
//                 e.preventDefault();
//                 window.location = $.param.querystring( window.location.href, 'debug');
//             });
//             new instance.web.Dialog(this, {
//                 size: 'medium',
//                 dialogClass: 'oe_act_window',
//                 title: _t("About"),
//             }, $help).open();
//         });
//     },