openerp.web_support_client = function (instance) {
    instance.web.UserMenu.include({
    do_update: function () {
        this._super.apply(this, arguments);
        var self = this;
        var fct = function() {
            var get_chat_values = new instance.web.Model("support.contract").get_func("get_chat_values");
            get_chat_values().then(function(values) {
                if(values)
                    if (!values.talkusID){
                        return;
                    }
                    if (!values.user_remote_partner_uuid){
                        return;
                    }
                    (function(t,a,l,k,u,s,_){if(!t[u]){t[u]=function(){(t[u].q=t[u].q||[]).push(arguments)},t[u].l=1*new Date();s=a.createElement(l),_=a.getElementsByTagName(l)[0];s.async=1;s.src=k;_.parentNode.insertBefore(s,_)}})(window,document,'script','//www.talkus.io/plugin.js','talkus');
                    if(values.talkus_image_url)
                        talkus('loadingImage', values.talkus_image_url);
                    if(values.user_image)
                        user_img = instance.session.url('/web/user/image', {user_id: values.user_id});
                    else
                        user_img = "";
                    talkus('create', values.talkusID);
                    talkus('identify', { id: values.user_remote_partner_uuid, name: values.user_name, email: values.user_email, picture: user_img});
                });
            };
        this.update_promise = this.update_promise.then(fct, fct);
        }
    })
}