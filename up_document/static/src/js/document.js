openerp.document = function (instance, m) {
}
//openerp.up_document = function (instance, m) {
//    var _t = instance.web._t,
//        QWeb = instance.web.qweb;
//
//    instance.web.form.FieldBinary.include({
//        on_save_as: function (ev) {
//            var value = this.get('value');
//            if (!value) {
//                this.do_warn(_t("Save As..."), _t("The field is empty, there's nothing to save !"));
//                ev.stopPropagation();
//            } else {
//                instance.web.blockUI();
//                var c = instance.webclient.crashmanager;
//                this.session.get_file({
//                    url: '/web/binary/saveas_ajax',
//                    data: {data: JSON.stringify({
//                        model: this.view.dataset.model,
//                        id: (this.view.datarecord.id || ''),
//                        field: this.name,
//                        filename_field: (this.node.attrs.filename || ''),
//                        data: instance.web.form.is_bin_size(value) ? null : value,
//                        context: this.view.dataset.get_context()
//                    })},
//                    complete: instance.web.unblockUI,
//                    error: function (error) {
//                        var error_json = JSON.parse(error[0].innerText);
////                        alert(error_json.message);
//                        c.rpc_error(error_json);
//                    }
//                });
//                ev.stopPropagation();
//                return false;
//            }
//        }
//    });
//};

