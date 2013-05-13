set_cookie: function (name, value, ttl) {
        if (!this.name) { return; }
        ttl = ttl || 24*60*60*365;
        document.cookie = [
            this.name + '|' + name + '=' + encodeURIComponent(JSON.stringify(value)),
            'path=/',
            'max-age=' + ttl,
            'expires=' + new Date(new Date().getTime() + ttl*1000).toGMTString(),
            'domain=.updis.cn'
        ].join(';');
    },