/**
 *
 * Created by cysnake4713 on 14-11-11.
 */

openerp.signature = function (instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web.form.FieldSignature = instance.web.form.FieldBinaryImage.extend({
        template: 'FieldSignature',
        placeholder: "/web/static/src/img/placeholder.png",
        render_value: function () {
            var self = this;
            var parent_render = this._super;
            self.effective_readonly = true;
            var user = this.get('value');
            if (user){
                new instance.web.Model('res.users').call('get_user_image', [user[0]]).done(function (result) {
                    //如果有签名图片，则显示签名图片，
                    if (result != null) {
                        var url = 'data:image/png;base64,' + result;
                        var $img = $(QWeb.render("FieldBinaryImage-img", { widget: self, url: url }));
                        self.$el.find('> img').remove();
                        self.$el.prepend($img);
                        $img.load(function () {
                            if (!self.options.size)
                                return;
                            $img.css("max-width", "" + self.options.size[0] + "px");
                            $img.css("max-height", "" + self.options.size[1] + "px");
                            $img.css("margin-left", "" + (self.options.size[0] - $img.width()) / 2 + "px");
                            $img.css("margin-top", "" + (self.options.size[1] - $img.height()) / 2 + "px");
                        });
                        $img.on('error', function () {
                            $img.attr('src', self.placeholder);
                            instance.webclient.notification.warn(_t("Image"), _t("Could not display the selected image."));
                        });
                        //如果没有签名图片，则显示用户名称。
                    } else {
                        self.$el.html(user[1]);
                    }
                });
            }
        },
    });

    instance.web.form.widgets.add('signature', 'instance.web.form.FieldSignature');
};
