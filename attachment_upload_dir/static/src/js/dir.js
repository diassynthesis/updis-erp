/**
 * Created by cysnake4713 on 14-7-12.
 */
openerp.attachment_upload_dir = function (instance) {

    var _lt = instance.web._lt;
    var _t = instance.web._t;

    instance.web.views.add('dir', 'instance.attachment_upload_dir.DirView');

    var WidgetManager = instance.web.Class.extend({

        read_fields: ['name'],

        get_widget: function (id) {
            var obj = new instance.web.Model('document.directory');
            return obj.call('read', [id, this.read_fields])
        }
    });

    instance.attachment_upload_dir.DirectoryWidget = instance.web.Widget.extend({
        template: 'DirectoryElement',
        widgetManager: new WidgetManager(),

        init: function (parent, directory) {
            this._super(parent, directory);
            this.directory = directory;
        },

        start: function (r) {
            this.bind_events();
            this._super();
        },

        bind_events: function () {
            this.$el.find("div.oe-line").hover(
                function () {
                    $(this).find("div.button-holder").css("visibility", "visible");
                },
                function () {
                    $(this).find("div.button-holder").css("visibility", "collapse");
                }
            );
            this.$el.find("div.arrow").click(function () {
                if ($(this).parent().parent().hasClass("oe_open") == true) {
                    $(this).parent().parent().removeClass("oe_open");
                } else {
                    $(this).parent().parent().addClass("oe_open oe_opened");
                }
            });
            this.$el.find("div.directory-line").dblclick(function () {
                if ($(this).parent().hasClass("oe_open") == true) {
                    $(this).parent().removeClass("oe_open");
                } else {
                    $(this).parent().addClass("oe_open oe_opened");
                }
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
                self.widgetManager.get_widget(id).done(function (result) {
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