/**
 * Created by cysnake4713 on 14-7-12.
 */
openerp.attachment_upload_dir = function (instance) {

    var _lt = instance.web._lt;
    var _t = instance.web._t;

    instance.web.views.add('dir', 'instance.attachment_upload_dir.DirView');

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
        }


    });


    instance.attachment_upload_dir.DocumentWidget = instance.web.Widget.extend({
        template: 'DocumentElement',
        widgetManager: new WidgetManager(),
        init: function (parent, document) {
            this._super(parent, document);
            this.document = document;
            this.dataset = parent.dataset;
        },
        start: function () {
            this.bind_events();
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
        }
    });

    instance.attachment_upload_dir.DirectoryWidget = instance.web.Widget.extend({
        template: 'DirectoryElement',
        widgetManager: new WidgetManager(),

        init: function (parent, directory) {
            this._super(parent, directory);
            this.directory = directory;
            this.dataset = parent.dataset;
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
        },
        create_child_directories: function () {
            var self = this;
            self.widgetManager.get_directory_child(self.directory.id, self.dataset.context).done(function (result) {
                _.each(result, function (directory) {
                    new instance.attachment_upload_dir.DirectoryWidget(self, directory).appendTo(self.$el.children('div.tree-child-holder').children('div.oe-directory-holder'));
                });
            });
        },
        create_child_documents: function () {
            var self = this;
            var res_id = self.dataset.context.default_res_id;
            var res_model = self.dataset.context.default_res_model;
            self.widgetManager.get_directory_documents(self.directory.id, res_id, res_model, self.dataset.context).done(function (result) {
                _.each(result, function (document) {
                    new instance.attachment_upload_dir.DocumentWidget(self, document).appendTo(self.$el.children('div.tree-child-holder').children('div.oe-document-holder'));
                });
            });
        }

    });

    instance.attachment_upload_dir.DirView = instance.web.View.extend({

        template: "DirView",
        display_name: _lt('Dir'),
        view_type: "dir",
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
                    new instance.attachment_upload_dir.DirectoryWidget(self, result).appendTo(self.$el.find('div.oe-document-tree'));
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