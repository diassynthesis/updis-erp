/**
 * Created with PyCharm.
 * User: Zhou Guangwen
 * Date: 3/17/13
 * Time: 6:40 PM
 * To change this template use File | Settings | File Templates.
 */

openerp.upcas = function (instance) {
    instance.web.SearchView = instance.web.SearchView.extend({
        init: function () {
            this._super.apply(this, arguments);
            this.on('search_data', this, function () {
                console.log('hello from cas!');
            });
        }
    });
    instance.web.WebClient = instance.web.WebClient.extend({
        on_logout: function () {
            console.log("Logout!!!")
            var self = this;
            if (!this.has_uncommitted_changes()) {
                self.rpc("/cas/cas_logout", {}).done(function (response) {
                    window.location = response["logout_url"];
                });
            }
        }
    })
    instance.web.JsonRPC = instance.web.JsonRPC.extend({
        rpc: function (url, params, options) {
            console.log(url);
            return this._supper.apply(this, arguments);
        }
    })
    instance.web.Login = instance.web.Login.extend({
        start: function () {
            var self = this;
            var d = $.when();
            if ($.deparam.querystring().ticket) {
                d = self.rpc("/cas/cas_login", {'ticket': $.deparam.querystring().ticket}).done(self.on_cas_loaded);
            } else {
                d = self.rpc("/cas/cas_login", {}).done(self.on_cas_loaded);
            }
            return d;
//            return this._super.apply(this, arguments);
        },
        on_cas_loaded: function (result) {
            var self = this;
            if (result.redirect_url) {
                window.location = result.redirect_url;
            } else {
                return self.do_login(result.db, result.username, result.password)
            }
        }
    })
}