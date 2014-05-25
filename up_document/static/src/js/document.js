openerp.document = function (instance, m) {
}
openerp.up_document = function (instance, m) {
    var _t = instance.web._t,
        QWeb = instance.web.qweb;

    instance.web.ListView.include({
        init: function (parent, dataset, view_id, options) {
            this._super.apply(this, arguments);
            $('div.oe_view_manager_sidebar').append("<div class='oe_multi_container'><div class='oe_sidebar multi_file_uploader_container'/></div>");
        },

        select_record: function (index, view) {
            this._super.apply(this, arguments);
            if (this.ViewManager.$el.find('div.multi_file_uploader_container')) {
                this.ViewManager.$el.find('div.multi_file_uploader_container').replaceWith("<div class='oe_sidebar multi_file_uploader_container'/>");
            }
        },

        view_loading: function (parent) {
            this._super.apply(this, arguments);
            var self = this;
            var model = parent.model;
            var type = parent.type;
            var context = this.dataset.context;
            var active_id = context.active_id;
            var active_model = context.active_model;
            var res_model = context.default_res_model ? context.default_res_model : '';
            var res_id = context.default_res_id ? context.default_res_id : 0;
            if (model == 'ir.attachment' && type == 'tree' && active_id && active_model == 'document.directory') {
                new qq.FileUploader({
                    element: this.ViewManager.$el.find('div.multi_file_uploader_container')[0],
                    action: '/web/clupload/multi_upload',
                    params: {
                        'session_id': openerp.instances.instance0.session.session_id,
                        'parent_id': active_id,
                        'res_model': res_model,
                        'res_id': res_id
                    },
                    uploadButtonText: "批量上传",
                    onComplete: function (id, fileName, responseJSON) {
                        if (responseJSON.success) {
                            self.reload();
                        } else {
                            instance.web.dialog($(QWeb.render("CrashManager.error", responseJSON)), {
                                width: '70%',
                                title: "上传文件出错!",
                                modal: true,
                                buttons: [
                                    {text: _t("Ok"), click: function () {
                                        $(this).dialog("close");
                                    }}
                                ]
                            });
                        }
                    }
                });
                this.ViewManager.$el.find('.multi_file_uploader_container div.qq-upload-button').bind('mouseover', function (e) {
                    $('.multi_file_uploader_container .qq-uploader .qq-upload-list').css('display', 'block');
                });
                $(document).bind('click', function () {
                    $('.multi_file_uploader_container .qq-uploader .qq-upload-list').css('display', 'none');
                })

            } else {
//                $('.oe_list_button_multi_upload').css('display', 'none');
//                $('.oe_list_span_multi_upload').css('display', 'none');
            }

        }

    });

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

    instance.web.form.FieldMany2ManyTags.include({
        _search_create_popup: function (view, ids, context) {
            var self = this;
            var pop = new instance.web.form.SelectCreatePopup(this);
            pop.select_element(
                self.field.relation,
                {
                    title: (view === 'search' ? _t("Search: ") : _t("Create: ")) + this.string,
                    initial_ids: ids ? _.map(ids, function (x) {
                        return x[0]
                    }) : undefined,
                    initial_view: view,
                    disable_multiple_selection: false
                },
                self.build_domain(),
                new instance.web.CompoundContext(self.build_context(), context || {})
            );
            pop.on("elements_selected", self, function (element_ids) {
                _.each(element_ids,function (element_id) {
                    self.add_id(element_id);
                });
                self.focus();
            });
        }
    });
};

