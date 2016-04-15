  (function(t,a,l,k,u,s,_){if(!t[u]){t[u]=function(){(t[u].q=t[u].q||[]).push(arguments)},t[u].l=1*new Date();s=a.createElement(l),_=a.getElementsByTagName(l)[0];s.async=1;s.src=k;_.parentNode.insertBefore(s,_)}})(window,document,'script','//www.talkus.io/plugin.js','talkus');
  talkus('loadingImage', 'https://www.adhoc.com.ar/website/image?field=datas&model=ir.attachment&id=1116');
  talkus('create', 'AKoBPjeu9YRvYHKQu');

(function() {

var instance = openerp;

instance.web.Notification =  instance.web.Widget.extend({

    init: function() {

        var func = new instance.web.Model("res.users").get_func("read");

			func(instance.session.uid, ["name",  "id", "email"]).then(function(res) {
			    talkus('identify', { id: res.name + "-" + res.id, name: res.name, email: res.email});
			});
    }

});


})();