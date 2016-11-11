odoo.define('web_support_client.talkus_chat', function(require) {
"use strict";
var UserMenu = require('web.UserMenu');
var Model = require('web.Model');
var session = require('web.session');
var user_img = "";
UserMenu.include({
    do_update: function(){
        this._super.apply(this, arguments);
        var fct = function() {
            var get_chat_values = new Model("support.contract").get_func("get_chat_values");
            get_chat_values().then(function(values) {
                if(values)
                    if (!values.talkusID){
                        return;
                    }
                    if (!values.user_remote_partner_uuid){
                        return;
                    }
                    (function(t,a,l,k,u,s,e){if(!t[u]){t[u]=function(){(t[u].q=t[u].q||[]).push(arguments)},t[u].l=1*new Date();s=a.createElement(l),e=a.getElementsByTagName(l)[0];s.async=1;s.src=k;e.parentNode.insertBefore(s,e)}})(window,document,'script','//www.talkus.io/plugin.beta.js','talkus');
                    if(values.user_image)
                        user_img = session.url('/web/user/image', {user_id: values.user_id});

                    talkus('init', values.talkusID, {id: values.user_remote_partner_uuid, name: values.user_name, email: values.user_email, picture: user_img});
                });
            };
        this.update_promise = this.update_promise.then(fct, fct);
        }
    });
});
