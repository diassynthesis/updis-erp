/**
 * Created with PyCharm.
 * User: Zhou Guangwen
 * Date: 3/24/13
 * Time: 3:29 PM
 * To change this template use File | Settings | File Templates.
 */
    cas_check: function (url_to_check) {
        var d = $.Deferred();
        if (url_to_check.substring(0,5) == "/cas/") {
            return d.resolve(null, null, null);
        }
        var self = this;
        var url = {url: "/cas/cas_login"};
        var payload = {
            jsonrpc: '2.0',
            method: 'call',
            id: _.uniqueId('r')
        };
        if ($.deparam.querystring().ticket) {
            payload.params = {'ticket': $.deparam.querystring().ticket};
        }
        this.rpc_function(url, payload).then(
            function (response, textStatus, jqXHR) {
                d.resolve(response["result"], textStatus, jqXHR);
            },
            function (response, textStatus, jqXHR) {
                d.reject(response.error, $.Event());
            }
        );
        return d;
    },
    rpc: function (url, params, options) {
        var self = this;
        return this.cas_check(url).then(function (response, textStatus, jqXHR) {
                if (response && response.redirect_url) {
                    window.location = response.redirect_url;
                } else {
                    if (response) {
                        self.set_cookie("session_id",response.session_id);
                    }
                    return self.do_rpc(url, params, options);
                }
            },
            function (response, textStatus, jqXHR) {
                console.log("Check is done with failure!");
//                    deferred.reject(response.error, $.Event());
                return;
            });
    },