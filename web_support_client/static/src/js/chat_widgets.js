function get_open_user() {

    var instance = openerp;

    instance.web.Notification =  instance.web.Widget.extend({

        // antes pasabamos el database uuid, ahora pasamos el de user
        init: function() {
            var func = new instance.web.Model("res.users").get_func("read");

                func(instance.session.uid, ["name",  "remote_partner_uuid", "email"]).then(function(res) {
                    if (res){
                        if (!res.remote_partner_uuid){
                            return;
                        }
                        (function(t,a,l,k,u,s,_){if(!t[u]){t[u]=function(){(t[u].q=t[u].q||[]).push(arguments)},t[u].l=1*new Date();s=a.createElement(l),_=a.getElementsByTagName(l)[0];s.async=1;s.src=k;_.parentNode.insertBefore(s,_)}})(window,document,'script','//www.talkus.io/plugin.js','talkus');
                        // TODO make this two parameters db parameters
                        talkus('loadingImage', 'https://www.adhoc.com.ar/website/image?field=datas&model=ir.attachment&id=1116');
                        talkus('create', 'AKoBPjeu9YRvYHKQu');
                        talkus('identify', { id: res.remote_partner_uuid, name: res.name, email: res.email});
                    }

            });
        }
        // init: function() {

        //     var config_parameter = new instance.web.Model('ir.config_parameter').get_func("get_param");
        //         config_parameter(['database.uuid', false]).then(function(dbuuid) {
        //             if (!dbuuid) {
        //                 return;
        //             }
        //         var func = new instance.web.Model("res.users").get_func("read");

        //             func(instance.session.uid, ["name",  "id", "email"]).then(function(res) {
        //                 if (res){
        //                     talkus('identify', { id: dbuuid + "-" + res.id, name: res.name, email: res.email});
        //                 }

        //         });
        //     });
        // }

    });

    var widget = new instance.web.Notification();


}

get_open_user();