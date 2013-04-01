openerp.updis = function(openerp) {
	var QWeb = openerp.web.qweb;	
	if (openerp.mail){
		openerp.mail.ThreadMessage.include({
			init: function (parent, datasets, options) {            
				this.is_anonymous = datasets.is_anonymous;
				return this._super(parent,datasets, options);
			},
			format_data:function(){
				ret = this._super.apply(this,arguments);
				if (this.is_anonymous) {
					this.avatar = ('/updis/static/src/img/anonymous.png');
				}
				return ret;
			}
		})
		openerp.mail.Thread.include({
			create_message_object: function (data) {
				var msg = this._super.apply(this,arguments);
				_.extend(msg.options,{'show_link':!data.is_anonymous});
				return msg;
			}
		})
		openerp.mail.ThreadComposeMessage.include({		
			do_send_message_post: function (partner_ids) {
				var self = this;
				this.parent_thread.ds_thread._model.call('message_post_user_api', [this.context.default_res_id], {
					'body': this.$('textarea').val(),
					'subject': false,
					'parent_id': this.context.default_parent_id,
					'attachment_ids': _.map(this.attachment_ids, function (file) {return file.id;}),
					'partner_ids': partner_ids,
					'context': this.parent_thread.context,
					'is_anonymous': this.$('.oe_is_anonymous').is(":checked"),
				}).done(function (message_id) {
					var thread = self.parent_thread;
					var root = thread == self.options.root_thread;
					if (self.options.display_indented_thread < self.thread_level && thread.parent_message) {
						var thread = thread.parent_message.parent_thread;
					}
					// create object and attach to the thread object
					thread.message_fetch([["id", "=", message_id]], false, [message_id], function (arg, data) {
						var message = thread.create_message_object( data[0] );
						// insert the message on dom
						thread.insert_message( message, root ? undefined : self.$el, root );
					});
					self.on_cancel();
				});
			}
		})
	};
}
