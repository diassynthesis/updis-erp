openerp.updis = function (instance, m) {
    var _t = instance.web._t,
        QWeb = instance.web.qweb;
    instance.mail.ThreadMessage.include({
        init: function (parent, datasets, options) {
            this._super(parent, datasets, options);
            this.is_anonymous = datasets.is_anonymous;
        },
        format_data: function () {
            this._super.apply(this, arguments);
            if (this.is_anonymous) {
                this.avatar = ('/updis/static/src/img/anonymous.png');
            }
        }
    });

    instance.mail.Thread.include({
        create_message_object: function (data) {
            var msg = this._super.apply(this,arguments);
            _.extend(msg.options, {'show_link': !data.is_anonymous});
            return msg;
        }
    });

    /* do post a message and fetch the message */

    instance.mail.ThreadComposeMessage.include({

        /* do post a message and fetch the message */
        do_send_message_post: function (partner_ids, log) {
            var self = this;
            var values = {
                'body': this.$('textarea').val(),
                'subject': false,
                'parent_id': this.context.default_parent_id,
                'attachment_ids': _.map(this.attachment_ids, function (file) {
                    return file.id;
                }),
                'partner_ids': partner_ids,
                'context': _.extend(this.parent_thread.context, {
                    'mail_post_autofollow': true,
                    'mail_post_autofollow_partner_ids': partner_ids
                }),
                'type': 'comment',
                'content_subtype': 'plaintext',
                'is_anonymous': this.$('.oe_is_anonymous').is(":checked")
            };
            if (log) {
                values['subtype'] = false;
            }
            else {
                values['subtype'] = 'mail.mt_comment';
            }
            this.parent_thread.ds_thread._model.call('message_post', [this.context.default_res_id], values).done(function (message_id) {
                var thread = self.parent_thread;
                var root = thread == self.options.root_thread;
                if (self.options.display_indented_thread < self.thread_level && thread.parent_message) {
                    var thread = thread.parent_message.parent_thread;
                }
                // create object and attach to the thread object
                thread.message_fetch([
                    ["id", "=", message_id]
                ], false, [message_id], function (arg, data) {
                    var message = thread.create_message_object(data[0]);
                    // insert the message on dom
                    thread.insert_message(message, root ? undefined : self.$el, root);
                });
                self.on_cancel();
                self.flag_post = false;
            });
        }

    })
}
