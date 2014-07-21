openerp.document = function (instance, m) {
}
openerp.up_document = function (instance, m) {
    var _t = instance.web._t,
        QWeb = instance.web.qweb;

    instance.web.form.FieldBinary.include({
        on_save_as: function (ev) {
            var value = this.get('value');
            if (!value) {
                this.do_warn(_t("Save As..."), _t("The field is empty, there's nothing to save !"));
                ev.stopPropagation();
            } else {
                instance.web.blockUI();
                var c = instance.webclient.crashmanager;
                this.session.get_file({
                    url: '/web/binary/saveas_ajax',
                    data: {data: JSON.stringify({
                        model: this.view.dataset.model,
                        id: (this.view.datarecord.id || ''),
                        field: this.name,
                        filename_field: (this.node.attrs.filename || ''),
                        data: instance.web.form.is_bin_size(value) ? null : value,
                        context: this.view.dataset.get_context()
                    })},
                    complete: instance.web.unblockUI,
                    error: function (error) {
                        var error_json = JSON.parse(error[0].innerText);
//                        alert(error_json.message);
                        c.rpc_error(error_json);
                    }
                });
                ev.stopPropagation();
                return false;
            }
        }
    });

    instance.web.list.Binary.include({
        format: function (row_data, options) {
            var text = _t("Download");
            var value = row_data[this.id].value;
            var download_url;
            var is_downloadable = 3;
            if (value && value.substr(0, 10).indexOf(' ') == -1) {
                download_url = "data:application/octet-stream;base64," + value;
            } else {
                download_url = instance.session.url('/web/binary/saveas', {model: options.model, field: this.id, id: options.id});
                if (this.filename) {
                    download_url += '&filename_field=' + this.filename;
                }
            }

            if (this.filename && row_data[this.filename] && row_data['is_downloadable'] && row_data['is_downloadable'].value < 3) {
                is_downloadable = row_data['is_downloadable'].value;
            }
            if (this.filename && row_data[this.filename]) {
                if (is_downloadable == 3) {
                    text = _.str.sprintf(_t("Download \"%s\""), instance.web.format_value(
                        row_data[this.filename].value, {type: 'char'}));
                } else {
                    text = _.str.sprintf(_t("\"%s\""), instance.web.format_value(
                        row_data[this.filename].value, {type: 'char'}));
                }

            }

            return QWeb.render('ListView.row.binary', {
                widget: this,
                prefix: instance.session.prefix,
                text: text,
                href: download_url,
                size: instance.web.binary_to_binsize(value),
                is_downloadable: is_downloadable
            });
        }
    });
};

