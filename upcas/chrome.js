on_logout: function () {
    var self = this;
    if (!this.has_uncommitted_changes()) {
        self.rpc("/cas/cas_logout", {}).done(function (response) {
            window.location = response["logout_url"];
        });
    }
}