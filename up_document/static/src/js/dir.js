/**
 * Created by cysnake4713 on 14-7-12.
 */
openerp.up_document = function (instance) {

    var _lt = instance.web._lt;
    var _t = instance.web._t;
    var Qweb = instance.web.qweb;

    instance.web.views.add('dir', 'instance.up_document.DirView');


    var WidgetManager = instance.web.Class.extend({

        get_directory: function (id, context) {
            var obj = new instance.web.Model('document.directory');
            return obj.call('get_directory_info', [id, {'context': context}])
        },
        get_directory_child: function (id, context) {
            var obj = new instance.web.Model('document.directory');
            return obj.call('get_directory_child_info', [id, {'context': context}])
        },
        get_directory_documents: function (directory_id, res_id, res_model, context) {
            var obj = new instance.web.Model('ir.attachment');
            return obj.call('get_directory_documents', [directory_id, res_id, res_model, {'context': context}])
        },
        delete_document: function (document_ids, context) {
            var obj = new instance.web.Model('ir.attachment');
            return obj.call('unlink', [document_ids, {'context': context}])
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
        },
        bind_data_events: function () {
            var self = this;
            self.$el.find('button.button-delete:first').click(function () {
                if (confirm('确认删除么？')) {
                    self.delete();
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
        delete: function () {
            var self = this;
            self.widgetManager.delete_document(self.document.id, self.dataset.context).done(function () {
                self.refresh_parent();
            });
        },
        refresh_parent: function () {
            this.parent.refresh_files();
        }
    });

    instance.up_document.DirectoryWidget = instance.web.Widget.extend({
        template: 'DirectoryElement',
        widgetManager: new WidgetManager(),

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
            self.$el.find("input.file-upload:first").fileupload({
                dataType: 'json',
                url: '/web/clupload/multi_upload',
                sequentialUploads: true,
                formData: data,
                done: function (e, data) {
                    if (data.result.files[0].error) {
                        instance.webclient.notification.warn(
                            _t("上传错误!"),
                            _t(data.result.files[0].error));
                    }
                },
                fail: function (e, data) {
                    instance.webclient.notification.warn(
                        _t("网络错误"),
                        _t("请检查传输情况并重新上传文件"));
                    // data.errorThrown
                    // data.textStatus;
                    // data.jqXHR;
                },
                progressall: function (e, data) {
//                    self.$el.find('div.oe-upload-holder:first').css('display','block');
                    var progress = parseInt(data.loaded / data.total * 100, 10);
                    var progress_template = Qweb.render('DocumentProcess', {'progress': progress});
                    self.$el.find('div.oe-upload-holder:first').html(progress_template);
                    if (progress == 100) {
                        if (self.$el.hasClass("oe_opened")) {
                            self.refresh_files();
                        }
                        self.$el.find('div.oe-upload-holder:first').html('');
                        instance.webclient.notification.notify(
                            _t("上传完成"),
                            _t(""));
                    }
                }
            });
        },
        bind_data_events: function () {
            var self = this;
            self.$el.find("div.arrow").click(function () {
                if (!self.$el.hasClass("oe_opened")) {
                    self.create_child_directories();
                    self.create_child_documents();
                    self.$el.addClass("oe_opened");
                }
            });
            self.$el.find("div.directory-line").dblclick(function () {
                if (!self.$el.hasClass("oe_opened")) {
                    self.create_child_directories();
                    self.create_child_documents();
                    self.$el.addClass("oe_opened");
                }
            });
            self.$el.find("button.button-refresh:first").click(function () {
                self.refresh_directories();
                self.refresh_files();
            });
        },
        create_child_directories: function () {
            var self = this;
            self.widgetManager.get_directory_child(self.directory.id, self.dataset.context).done(function (result) {
                _.each(result, function (directory) {
                    var dir = new instance.up_document.DirectoryWidget(self, directory);
                    self.child_directories = self.child_directories.concat(dir);
                    dir.appendTo(self.$el.children('div.tree-child-holder').children('div.oe-directory-holder'));
                });
            });
        },
        create_child_documents: function () {
            var self = this;
            var res_id = self.dataset.context.res_id;
            var res_model = self.dataset.context.res_model;
            self.widgetManager.get_directory_documents(self.directory.id, res_id, res_model, self.dataset.context).done(function (result) {
                _.each(result, function (document) {
                    var file = new instance.up_document.DocumentWidget(self, document);
                    self.child_files = self.child_files.concat(file);
                    file.appendTo(self.$el.children('div.tree-child-holder').children('div.oe-document-holder'));
                });
            });
        },
        refresh_files: function () {
            _.each(this.child_files, function (file) {
                file.destroy();
            });
            this.create_child_documents();
        },
        refresh_directories: function () {
            _.each(this.child_directories, function (dir) {
                dir.destroy();
            });
            this.create_child_directories();
        },
        multi_upload: function (parent) {
            B

        }

    });

    instance.up_document.DirView = instance.web.View.extend({

        template: "DirView",
        display_name: _lt('Dir'),
        view_type: "dir",
        searchable: false,
        widgetManager: new WidgetManager(),

        init: function (parent, dataset, view_id, options) {
            this._super(parent);
            this.set_default_options(options);
            this.dataset = dataset;
            this.view_id = view_id;
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
                self.widgetManager.get_directory(id, self.dataset.context).done(function (result) {
                    new instance.up_document.DirectoryWidget(self, result).appendTo(self.$el.find('div.oe-document-tree'));
                });
            });

        },
        destroy: function () {
            if (this.dir) {
                this.dir.destroy();
            }
            this._super();
        }
    });
};