// Esta alternativa no nos anduvo
// openerp.adhoc_modules = function (instance) {
//     instance.web.ActionManager = instance.web.ActionManager.extend({

//         ir_actions_act_close_wizard_and_reload_view: function (action, options) {
//             if (!this.dialog) {
//                 options.on_close();
//             }
//             this.dialog_stop();
//             // this.inner_widget.views[this.inner_widget.active_view].controller.reload();
//             this.inner_widget.active_view.controller.reload();
//             // this.inner_widget.active_view.controller.reload();
//             return $.when();
//         },
//     });
// }
openerp.adhoc_modules = function(instance, local) {
    var bus = instance.bus.bus;
    bus.add_channel("<CHANNEL-NAME>");   
    // });
};
openerp.adhoc_modules = function(instance, local) {
    var bus = instance.bus.bus;
    bus.add_channel("<CHANNEL-NAME>");
    instance.bus.bus.on("notification", instance, function(notification){
        instance.client.action_manager.inner_widget.views["kanban"].controller.do_reload();
    });
};
