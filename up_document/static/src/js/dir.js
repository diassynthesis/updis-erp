/**
 * Created by cysnake4713 on 14-7-12.
 */
openerp.up_document = function (instance) {

    var _lt = instance.web._lt;
    var _t = instance.web._t;
    var Qweb = instance.web.qweb;

    instance.web.views.add('dir', 'instance.up_document.DirView');


    var WidgetManager = instance.web.Class.extend({

        get_directory: function (id, res_id, res_model, context) {
            var obj = new instance.web.Model('document.directory');
            return obj.call('get_directory_info', [id, res_id, res_model, context])
        },
        get_directory_child: function (id, res_id, res_model, context) {
            var obj = new instance.web.Model('document.directory');
            return obj.call('get_directory_child_info', [id, res_id, res_model, context])
        },
        get_directory_documents: function (directory_id, res_id, res_model, context) {
            var obj = new instance.web.Model('ir.attachment');
            return obj.call('get_directory_documents', [directory_id, res_id, res_model, context])
        },
        delete_document: function (document_ids, res_id, res_model, context) {
            var obj = new instance.web.Model('ir.attachment');
            return obj.call('unlink_attachment', [document_ids, res_id, res_model, context])
        }


    });


    instance.up_document.DocumentWidget = instance.web.Widget.extend({
        template: 'DocumentElement',
        widgetManager: new WidgetManager(),
        init: function (parent, document) {
            this._super(parent, document);
            this.document = document;
            this.dataset = parent.dataset;
            this.parent = parent;
            this.document.url = instance.session.url('/web/binary/saveas', {model: 'ir.attachment', 'filename_field': 'name', field: 'datas', id: this.document.id});
        },
        start: function () {
            this.bind_events();
            this.bind_data_events();
            this._super();
        },
        bind_events: function () {
            var self = this;
            self.$el.hover(
                function () {
                    $(this).find("div.button-holder").css("visibility", "visible");
                },
                function () {
                    $(this).find("div.button-holder").css("visibility", "collapse");
                }
            );
            self.$el.find("div.document-select > input[name=radiogroup]").change(function (e) {
                if (this.checked == false) {
                    self.parent.set_not_total_selected();
                }
            });
        },
        bind_data_events: function () {
            var self = this;
            self.$el.find('button.button-delete:first').click(function () {
                if (confirm('确认删除么？')) {
                    self.delete_file();
                }
            });
            self.$el.find('button.button-detail:first').click(function () {
                self.do_action({
                    type: 'ir.actions.act_window',
                    res_model: 'ir.attachment',
                    res_id: self.document.id,
                    views: [
                        [false, 'form']
                    ],
                    target: 'current',
                    context: self.dataset.context
                });
                return false;
            });
        },
        delete_file: function () {
            var self = this;
            self.widgetManager.delete_document(self.document.id, self.dataset.context.res_id, self.dataset.context.res_model, self.dataset.context).done(function () {
                self.parent.delete_document(self);
            });
        },
        is_selected: function () {
            return this.$el.find("div.document-select > input[name=radiogroup]:first")[0].checked;
        }
    });

    instance.up_document.DirectoryWidget = instance.web.Widget.extend({
        template: 'DirectoryElement',
        widgetManager: new WidgetManager(),
        events: {
            "click div.arrow": "create_children_elements",
            "dblclick div.directory-line": "create_children_elements",
            "dragover div.directory-line": function(){
                this.$el.children("div.directory-line:first").addClass('dragenter');
            },
            "dragleave div.directory-line": function(){
                this.$el.children("div.directory-line:first").removeClass('dragenter');
            },
            "drop div.directory-line": function(){
                this.$el.children("div.directory-line:first").removeClass('dragenter');
            },
        },

        init: function (parent, directory) {
            this._super(parent, directory);
            this.directory = directory;
            this.dataset = parent.dataset;
            this.parent = parent;
            this.child_directories = [];
            this.child_files = [];
        },

        start: function (r) {
            this.bind_events();
            this.bind_data_events();
            this._super();
        },

        bind_events: function () {
            var self = this;
            self.$el.find("div.oe-line").hover(
                function () {
                    $(this).find("div.button-holder").css("visibility", "visible");
                },
                function () {
                    $(this).find("div.button-holder").css("visibility", "collapse");
                }
            );
            self.$el.find("div.arrow").click(function () {
                if (self.$el.hasClass("oe_open") == true) {
                    self.$el.removeClass("oe_open");
                } else {
                    self.$el.addClass("oe_open");
                }
            });
            self.$el.find("div.directory-line").dblclick(function () {
                if (self.$el.hasClass("oe_open") == true) {
                    self.$el.removeClass("oe_open");
                } else {
                    self.$el.addClass("oe_open");
                }
            });
            self.$el.find("button.button-upload:first").click(function (e) {
                self.$el.find("input.file-upload:first").click();
                e.preventDefault();
            });
            self.bind_data_upload();
            self.$el.find("div.directory-select > input:checkbox:first").change(function (e) {
                self.$el.find("input[name=radiogroup]").attr('checked', this.checked);
                if (this.checked == false) {
                    self.parent.set_not_total_selected();
                }
            });
        },
        bind_data_events: function () {
            var self = this;
            self.$el.find("button.button-refresh:first").click(function () {
                self.set_not_total_selected();
                $.when(self.refresh_directories(), self.refresh_files(), self.refresh_self()).done(function () {
                    self.draw();
                });
            });
        },
        refresh_self: function () {
            var self = this;
            self.widgetManager.get_directory(self.directory.id, self.dataset.context.res_id, self.dataset.context.res_model, self.dataset.context).done(function (result) {
                self.directory = result;
                //refresh self filed number
                self.$el.find('div.tips:first').html(self.directory.file_total + '个文件');
            });
        },
        create_children_elements: function () {
            var self = this;
            if (!self.is_opened()) {
                $.when(self.create_child_directories(), self.create_child_documents()).done(function () {
                    self.draw();
                    self.is_opened(true);
                    //sync checkbox status
                    self.$el.find("input[name=radiogroup]").attr('checked',
                        self.$el.children("div.directory-line").find(".directory-select > input:checkbox")[0].checked);
                });
            }
        },
        is_opened: function (value) {
            if (value == true) {
                this.$el.addClass("oe_opened");
            } else if (value == false) {
                this.$el.removeClass("oe_opened");
            }
            return this.$el.hasClass("oe_opened")
        },
        delete_document: function (document) {
            var self = this;
            _.each(self.child_files, function (file, i) {
                if (file == document) {
                    self.child_files.splice(i, 1);
                    file.destroy();
                }
            });
            self.refresh_self();
        },
        bind_data_upload: function () {
            var self = this;
            var data = {
                parent_id: self.directory.id,
                session_id: openerp.instances.instance0.session.session_id
            };
            if (self.dataset.context.res_id) {
                data.res_id = self.dataset.context.res_id;
            }
            if (self.dataset.context.res_model) {
                data.res_model = self.dataset.context.res_model;
            }
            var total_progress = 0;
            self.$el.find("input.file-upload:first").fileupload({
                dataType: 'json',
                url: '/web/clupload/multi_upload',
                sequentialUploads: true,
                formData: data,
                dropZone: this.$el.find("div.directory-line:first"),
                add: function (e, data) {
                    var uploadFile = data.files[0];
                    if (uploadFile.size > 2048 * 1024 * 1024) { // 2mb
                        instance.webclient.notification.warn(
                            _t("文件过大!"),
                            _t("上传文件超过2GB！请分卷压缩后上传。"));
                    } else {
                        instance.web.blockUI();
                        data.submit();
                    }
                },
                done: function (e, data) {
                    if (data.result.files[0].error) {
                        instance.webclient.notification.warn(
                            _t("上传错误!"),
                            _t(data.result.files[0].error));
                    }
                    if (total_progress == 90) {
                        instance.web.unblockUI();
                        if (self.is_opened()) {
                            self.refresh_files().done(function () {
                                self.draw();
                                self.refresh_self();
                            });
                        }
                        self.$el.find('div.oe-upload-holder:first').html('');
                        instance.webclient.notification.notify(
                            _t("上传完成"),
                            _t(""));
                    }
                },
                fail: function (e, data) {
                    instance.web.unblockUI();
                    instance.webclient.notification.warn(
                        _t("网络错误"),
                        _t("请检查传输情况并重新上传文件"));
                    self.$el.find('div.oe-upload-holder:first').html('');
                },
                progressall: function (e, data) {
                    total_progress = parseInt(data.loaded / data.total * 90, 10);
                    var progress_template = Qweb.render('DocumentProcess', {'progress': total_progress});
                    self.$el.find('div.oe-upload-holder:first').html(progress_template);
                }
            });
        },
        create_child_directories: function () {
            var self = this;
            return self.widgetManager.get_directory_child(self.directory.id, self.dataset.context.res_id, self.dataset.context.res_model, self.dataset.context).done(function (result) {
                _.each(result, function (directory) {
                    var dir = new instance.up_document.DirectoryWidget(self, directory);
                    self.child_directories = self.child_directories.concat(dir);
                });
            });
        },
        create_child_documents: function () {
            var self = this;
            var res_id = self.dataset.context.res_id;
            var res_model = self.dataset.context.res_model;
            return self.widgetManager.get_directory_documents(self.directory.id, res_id, res_model, self.dataset.context).done(function (result) {
                _.each(result, function (document) {
                    var file = new instance.up_document.DocumentWidget(self, document);
                    self.child_files = self.child_files.concat(file);
                });
            });
        },
        draw: function () {
            var self = this;
            self.$el.children('div.tree-child-holder').children('div.oe-directory-holder').html("");
            self.$el.children('div.tree-child-holder').children('div.oe-document-holder').html("");
            _.each(self.child_directories, function (dir) {
                dir.appendTo(self.$el.children('div.tree-child-holder').children('div.oe-directory-holder'));
            });
            _.each(self.child_files, function (file) {
                file.appendTo(self.$el.children('div.tree-child-holder').children('div.oe-document-holder'));
            });
        },
        refresh_directories: function () {
            _.each(this.child_directories, function (dir) {
                dir.destroy();
            });
            this.child_directories = [];
            return this.create_child_directories();
        },
        refresh_files: function () {
            _.each(this.child_files, function (file) {
                file.destroy();
            });
            this.set_not_total_selected();
            this.child_files = [];
            return this.create_child_documents();
        },
        set_not_total_selected: function () {
            this.$el.find("div.directory-select > input:checkbox:first").attr('checked', false);
            this.parent.set_not_total_selected();
        },
        get_child_select_files: function () {
            var self = this;
            var file_ids = [];
            var directory_ids = [];

            _.each(self.child_files, function (file) {
                if (file.is_selected()) {
                    file_ids = _.union(file_ids, file.document.id);
                }
            });
            _.each(self.child_directories, function (directory) {
                if (directory.is_selected()) {
                    directory_ids = _.union(directory_ids, directory.directory.id);
                } else if (directory.is_opened()) {
                    var result = directory.get_child_select_files();
                    file_ids = _.union(file_ids, result[0]);
                    directory_ids = _.union(directory_ids, result[1]);
                }
            });
            return [file_ids, directory_ids];
        },
        destroy: function () {
            _.each(self.child_directories, function (dir) {
                dir.destory();
            });
            _.each(self.child_files, function (file) {
                file.destory();
            });
            this.child_directories = [];
            this.child_files = [];
            this._super();
        },
        is_selected: function () {
            return this.$el.find("div.directory-select > input[name=radiogroup]:first")[0].checked;
        }
    });

    instance.up_document.DirView = instance.web.View.extend({

        template: "DirView",
        display_name: _lt('Dir'),
        view_type: "dir",
        searchable: false,
        widgetManager: new WidgetManager(),
        events: {
            "click button.download": "download_file",
            "click button.download-apply": 'download_apply_file',
        },

        init: function (parent, dataset, view_id, options) {
            this._super(parent);
            this.set_default_options(options);
            this.dataset = dataset;
            this.view_id = view_id;
            this.child_directories = [];
//            this.mode = "bar";          // line, bar, area, pie, radar
//            this.orientation = false;    // true: horizontal, false: vertical
//            this.stacked = true;
//
//            this.spreadsheet = false;   // Display data grid, allows copy to CSV
//            this.forcehtml = false;
//            this.legend = "top";        // top, inside, no
//
            this.domain = [];
            this.context = [];
            this.group_by = [];
//
            this.dir = null;
            this.datas = [];
        },

        view_loading: function (r) {
            return this.load_dir();
        },

        load_dir: function () {
            var self = this;
            self.dir_get_data().done(function (result) {
                self.dir_render_all(result);
            });
        },
        download_apply_file: function () {
            var self = this;
            var ids = self.get_need_process_files();
            var context = self.dataset.context;
            var res_id = self.dataset.context.res_id;
            var res_model = self.dataset.context.res_model;

            new instance.web.Model('ir.attachment').call('get_download_apply_file', [ids[0], ids[1], res_id, res_model, context]).done(function (result) {
                if (result.length == 0) {
                    alert("没有选择可审评的文件");
                } else {
                    context.attachment_ids = result;
                    self.do_action({
                        type: 'ir.actions.act_window',
                        src_model: 'ir.attachment',
                        res_model: 'ir.attachment.application',
                        views: [
                            [false, 'form']
                        ],
                        target: 'new',
                        context: context
                    });
                }
            });
        },
        download_file: function (e) {
            var self = this;
            var ids = self.get_need_process_files();
            var context = self.dataset.context;
            var res_id = self.dataset.context.res_id;
            var res_model = self.dataset.context.res_model;

            new instance.web.Model('ir.attachment').call('get_download_file', [ids[0], ids[1], res_id, res_model, context]).done(function (result) {
                context.active_ids = result;
                self.do_action({
                    type: 'ir.actions.act_window',
                    src_model: 'ir.attachment',
                    res_model: 'ir.attachment.download.wizard',
                    views: [
                        [false, 'form']
                    ],
                    target: 'new',
                    context: context
                });
            });
        },
        get_need_process_files: function () {
            var self = this;
            var file_ids = [];
            var directory_ids = [];
            _.each(self.child_directories, function (directory) {
                if (directory.is_selected()) {
                    directory_ids = _.union(directory_ids, directory.directory.id);
                } else if (directory.is_opened()) {
                    var result = directory.get_child_select_files();
                    file_ids = _.union(file_ids, result[0]);
                    directory_ids = _.union(directory_ids, result[1]);
                }
            });
            return [file_ids, directory_ids];
        },

        dir_get_data: function () {
            var model = this.dataset.model,
                domain = this.dataset.domain,
                context = this.dataset.context;

            var dir_obj = new instance.web.Model(model);
            var result = [];

            return dir_obj.call('search', [domain]).then(function (obj_ids) {
                return obj_ids;
            });

        },
        dir_render_all: function (ids) {
            var self = this;
            _.each(ids, function (id) {
                self.widgetManager.get_directory(id, self.dataset.context.res_id, self.dataset.context.res_model, self.dataset.context).done(function (result) {
                    var dir = new instance.up_document.DirectoryWidget(self, result);
                    self.child_directories = self.child_directories.concat(dir);
                    dir.appendTo(self.$el.find('div.oe-document-tree'));
                });
            });

        },
        destroy: function () {
            if (this.dir) {
                this.dir.destroy();
            }
            this._super();
        },

        set_not_total_selected: function () {
        }
    });


    instance.web.list.BigBinary = instance.web.list.Column.extend({
        /**
         * Return a link to the binary data as a file
         *
         * @private
         */
        _format: function (row_data, options) {
            var text = _t("Download");
            var download_url;
            var size = 0;
            download_url = instance.session.url('/web/binary/saveas', {model: options.model, field: 'name', id: options.id});
            if (this.filename) {
                size = instance.web.human_size(row_data[this.filename].value);
            }
            download_url += '&filename_field=' + this.id;
            text = _.str.sprintf(_t("Download \"%s\""), instance.web.format_value(
                row_data[this.id].value, {type: 'char'}));
            return _.template('<a href="<%-href%>"><%-text%></a> (<%-size%>)', {
                text: text,
                href: download_url,
                size: size
            });
        }
    });


    instance.web.list.columns.add('field.bigbinary', 'instance.web.list.BigBinary');

    instance.web.form.BigBinary = instance.web.form.FieldBinaryFile.extend({
        template: 'BigFieldBinaryFile',
        initialize_content: function () {
            var self = this;
            this._super();
            this.$el.find('button.oe_field_button:first').click(this.on_file_update);
            this.$el.find('input.oe_form_binary_file:first').css('z-index', -99);
            this.max_upload_size = 1024 * 1024 * 1024;
            var data = {
                session_id: openerp.instances.instance0.session.session_id,
                attachment_id: self.view.datarecord.id
            };
            if (!this.view.datarecord.id) {
                instance.webclient.notification.warn(
                    _t("文件尚未创建!"),
                    _t("请先保存文件一次，再进行上传操作！"));
            }
            var total_progress = 0;
            self.$el.find("input.file-upload:first").fileupload({
                dataType: 'json',
                url: '/web/binary/update_attachment',
                sequentialUploads: false,
                formData: data,
                add: function (e, data) {
                    var uploadFile = data.files[0];
                    if (uploadFile.size > 2048 * 1024 * 1024) { // 2mb
                        instance.webclient.notification.warn(
                            _t("文件过大!"),
                            _t("上传文件超过2GB！请分卷压缩后上传。"));
                    } else {
                        instance.web.blockUI();
                        data.submit();
                    }
                },
                done: function (e, data) {
                    if (data.result.files[0].error) {
                        instance.webclient.notification.warn(
                            _t("上传错误!"),
                            _t(data.result.files[0].error));
                    }
                    if (total_progress == 100) {
                        instance.web.unblockUI();
                        self.$el.find('div.oe-upload-holder:first').html('');
                        instance.webclient.notification.notify(
                            _t("上传完成"),
                            _t(""));
                    }
                    self.$el.find('input.field_binary:first').val(data.files[0].name);
                },
                fail: function (e, data) {
                    instance.web.unblockUI();
                    instance.webclient.notification.warn(
                        _t("网络错误"),
                        _t("请检查传输情况并重新上传文件"));
                    self.$el.find('div.oe-upload-holder:first').html('');
                },
                progressall: function (e, data) {
                    total_progress = parseInt(data.loaded / data.total * 100, 10);
                    var progress_template = Qweb.render('DocumentProcess', {'progress': total_progress});
                    self.$el.find('div.oe-upload-holder:first').html(progress_template);
                }
            });
        },
        on_file_update: function (e) {
            e.preventDefault();
            this.$el.find("input.file-upload:first").click();
        },
        on_file_change: function (e) {

        }
    });

    instance.web.form.TempFile = instance.web.form.AbstractField.extend(instance.web.form.ReinitializeFieldMixin, {
        template: 'TempFile',
        events: {
            'click a.download_url': 'download',
        },
        download: function (ev) {
            var value = this.get('value');
            if (!value) {
                this.do_warn(_t("Save As..."), _t("The field is empty, there's nothing to save !"));
                ev.stopPropagation();
            } else {
                instance.web.blockUI();
                var c = instance.webclient.crashmanager;
                this.session.get_file({
                    url: '/web/binary/download_temp_file',
                    data: {filename: value},
                    complete: instance.web.unblockUI,
                    error: c.rpc_error.bind(c)
                });
                ev.stopPropagation();
                return false;
            }
        },
    });

    instance.web.form.widgets.add('bigbinary', 'instance.web.form.BigBinary');
    instance.web.form.widgets.add('tempfile', 'instance.web.form.TempFile');
};