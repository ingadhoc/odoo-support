function get_open_user() {

    var instance = openerp;

    instance.web.Notification =  instance.web.Widget.extend({
        init: function() {
            var get_chat_values = new instance.web.Model("support.contract").get_func("get_chat_values");
            get_chat_values().then(function(values) {
                if(values)
                    // console.log('sadas')
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
                        user_img = instance.session.url('/web/binary/image', {model:'res.users', field: 'image_small', id: values.user_id});
                    else
                        user_img = "";
                    // user_img = "http://librerialogos.com.ar/images/marca.png";
                    talkus('create', values.talkusID);
                    // user_img = "https://www.adhoc.com.ar/web/binary/image?model=res.users&field=image_small&id=7"
                    // do not send user_img for now
                    talkus('identify', { id: values.user_remote_partner_uuid, name: values.user_name, email: values.user_email});
                    // talkus('identify', { id: values.user_remote_partner_uuid, name: values.user_name, email: values.user_email, picture: user_img});
            });
        }
    });
    var widget = new instance.web.Notification();
}

get_open_user();