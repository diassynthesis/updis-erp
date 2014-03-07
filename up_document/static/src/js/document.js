openerp.document = function (instance, m) {
}
openerp.up_document = function (instance, m) {
    var _t = instance.web._t,
        QWeb = instance.web.qweb;

//    instance.web.Sidebar.include({
//        init: function (parent) {
//            var model = parent.dataset ? parent.dataset.model : undefined;
//            var template = parent.__template__;
//            if (model == 'ir.attachment' && template == 'ListView') {
//                var self = this;
//                this._super.apply(this, arguments);
//                $('.oe_view_manager_sidebar').after(QWeb.render('AddGoogleDocumentItem', {widget: self}))
//                $('.oe_sidebar_add_multi_doc').bind('click', function (e) {
//                    alert('asdf');
//                });
//            } else {
//                this._super.apply(this, arguments);
//            }
//
//        },
//        on_google_doc: function () {
//            var self = this;
//            var view = self.getParent();
//            var ids = ( view.fields_view.type != "form" ) ? view.groups.get_selection().ids : [ view.datarecord.id ];
//            if (!_.isEmpty(ids)) {
//                view.sidebar_eval_context().done(function (context) {
//                    var ds = new instance.web.DataSet(this, 'ir.attachment', context);
//                    ds.call('google_doc_get', [view.dataset.model, ids, context]).done(function (r) {
//                        if (r == 'False') {
//                            var params = {
//                                error: response,
//                                message: _t("The user google credentials are not set yet. Contact your administrator for help.")
//                            }
//                            $(openerp.web.qweb.render("DialogWarning", params)).dialog({
//                                title: _t("User Google credentials are not yet set."),
//                                modal: true
//                            });
//                        }
//                    }).done(function (r) {
//                        window.open(r.url, "_blank");
//                        view.reload();
//                    });
//                });
//            }
//        }
//    });
    instance.web.ListView.prototype.import_enabled = false;
    instance.web.ListView.include({
        load_list: function (parent) {
            var add_button = false;
            if (!this.$buttons) {
                add_button = true;
            }
            this._super.apply(this, arguments);
            if (add_button) {
                this.$buttons.on('click', '.oe_list_button_multi_upload', function () {
//                    self.do_action({
//                        type: 'ir.actions.client',
//                        tag: 'import',
//                        params: {
//                            model: self.dataset.model
//                        }
//                    }, {
//                        on_reverse_breadcrumb: function () {
//                            self.reload();
//                        },
//                    });
                    alert('aa');
                    return false;
                });
            }
            var model = parent.model;
            var type = parent.type;
            if (model == 'ir.attachment' && type == 'tree') {


            } else {
                $('.oe_list_button_multi_upload').css('display', 'none');
                $('.oe_list_span_multi_upload').css('display', 'none');
            }

        }
    });
};

