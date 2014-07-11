/**
 * Created by cysnake4713 on 14-7-12.
 */
openerp.attachment_upload_dir = function (instance) {
    var _lt = instance.web._lt;
    var _t = instance.web._t;

    instance.web.views.add('dir', 'instance.attachment_upload_dir.DirView');

    instance.attachment_upload_dir.DirView = instance.web.View.extend({
        template: "",
        display_name: _lt('Dir'),
        view_type: "dir",

        init: function (parent, dataset, view_id, options) {
            var self = this;
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
            this.context = {};
            this.group_by = [];
//
//            this.graph = null;
        }
    });
};