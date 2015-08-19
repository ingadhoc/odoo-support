openerp.server_mode = function(instance) {
    _t = instance.web._t;
    instance.web.WebClient.include({
        show_application: function() {
            return $.when(this._super.apply(this, arguments)).then(this.proxy('show_mode_bar'));
            
        },
        show_mode_bar: function() {
            $(openerp.qweb.render('WebClient.mode_bar')).prependTo($('body'));
            var $bar = $('.mode_bar');
            $bar.css('display', 'none');
            $mode_message = $('.mode_message');
            this.rpc("/web/mode/get_mode", {'db': this.session.db, 'mode': 'test'}).always(function (ret_val){
                if (ret_val){
                    $mode_message.text('TEST')
                }
            })
            this.rpc("/web/mode/get_mode", {'db': this.session.db, 'mode': 'develop'}).always(function (ret_val){
                if (ret_val){
                    $mode_message.text('DEVELOP')
                }
            })
        }
    });
}
