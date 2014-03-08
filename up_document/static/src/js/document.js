openerp.document = function (instance, m) {
}
openerp.up_document = function (instance, m) {
    var _t = instance.web._t,
        QWeb = instance.web.qweb;

    instance.web.ListView.include({
        init: function (parent, dataset, view_id, options) {
            this._super.apply(this, arguments);
            $('div.oe_view_manager_sidebar').after("<div class='oe_sidebar multi_file_uploader_container'/>")
        },

        select_record: function (index, view) {
            this._super.apply(this, arguments);
            if (this.ViewManager.$el.find('div.multi_file_uploader_container')) {
                this.ViewManager.$el.find('div.multi_file_uploader_container').replaceWith("<div class='oe_sidebar multi_file_uploader_container'/>");
            }
        },

        view_loading: function (parent) {
            this._super.apply(this, arguments);
            var model = parent.model;
            var type = parent.type;
            var context = this.dataset.context;
            var active_id = context.active_id;
            var active_model = context.active_model;
            var res_model = context.default_res_model ? context.default_res_model : '';
            var res_id = context.default_res_id ? context.default_res_id : 0;
            if (model == 'ir.attachment' && type == 'tree' && active_id && active_model == 'document.directory') {
                var uploader = new qq.FileUploader({
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
                        } else {
                            alert('上传文件出错!\n' + responseJSON.error);
                        }
                    }
                });

            } else {
//                $('.oe_list_button_multi_upload').css('display', 'none');
//                $('.oe_list_span_multi_upload').css('display', 'none');
            }

        }

    });
};

