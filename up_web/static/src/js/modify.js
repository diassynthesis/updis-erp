/**
 * Created by cysnake4713 on 13-10-23.
 */

openerp.up_web = function (instance) {
    instance.web.CrashManager.include({
        rpc_error: function (error) {
            if (!this.active) {
                return;
            }
            // yes, exception handling is shitty
            if (error.code === 300 && error.data && error.data.type == "client_exception" && error.data.debug.match("SessionExpiredException")) {
                this.show_warning({type: "Session Expired", data: { fault_code: "登录过期，请重新刷新页面！" }});
                return;
            }
            if (error.data.fault_code) {
                var split = ("" + error.data.fault_code).split('\n')[0].split(' -- ');
                if (split.length > 1) {
                    error.type = split.shift();
                    error.data.fault_code = error.data.fault_code.substr(error.type.length + 4);
                }
            }
            if (error.code === 200 && error.type) {
                this.show_warning(error);
            } else {
                this.show_error(error);
            }
        },
        show_warning: function (error) {
            if (!this.active) {
                return;
            }
            instance.web.dialog($('<div>' + QWeb.render('CrashManager.warning', {error: error}) + '</div>'), {
                title: "UpdisERP " + _.str.capitalize(error.type),
                buttons: [
                    {text: _t("Ok"), click: function () {
                        $(this).dialog("close");
                    }}
                ]
            });
        },
        show_error: function (error) {
            if (!this.active) {
                return;
            }
            var buttons = {};
            buttons[_t("Ok")] = function () {
                $(this).dialog("close");
            };
            var dialog = new instance.web.Dialog(this, {
                title: "UpdisERP " + _.str.capitalize(error.type),
                width: '80%',
                height: '50%',
                min_width: '800px',
                min_height: '600px',
                buttons: buttons
            }).open();
            dialog.$el.html(QWeb.render('CrashManager.error', {session: instance.session, error: error}));
        }
    });

    instance.web.WebClient.include({
        set_title: function (title) {
            title = _.str.clean(title);
            var sep = _.isEmpty(title) ? '' : ' - ';
            document.title = title + sep + 'UpdisERP';
        },
        on_logout: function () {
            var self = this;
            var logout_url = $("#openerp-logout-url").text();
            if (!this.has_uncommitted_changes()) {
                this.session.session_logout().done(function () {
                    $(window).unbind('hashchange', self.on_hashchange);
                    self.do_push_state({});
                    if (logout_url == "") {
                        window.location.reload();
                    } else {
                        window.location = logout_url;
                    }
                });
            }
        }
    });


    instance.web.Session.include({
        /**
         * Create a new cookie with the provided name and value
         *
         * @private
         * @param name the cookie's name
         * @param value the cookie's value
         * @param ttl the cookie's time to live, 1 year by default, set to -1 to delete
         */
        set_cookie: function (name, value, ttl) {
            if (!this.name) {
                return;
            }
            ttl = ttl || 24 * 60 * 60 * 365;
            var domain = $('#openerp-domain-value').text();
            document.cookie = [
                this.name + '|' + name + '=' + encodeURIComponent(JSON.stringify(value)),
                'path=/',
                'max-age=' + ttl,
                'expires=' + new Date(new Date().getTime() + ttl * 1000).toGMTString(),
                'domain=' + domain
            ].join(';');
        }
    });

    instance.web.form.FieldTextHtml.include({
        initialize_content: function () {
            var self = this;
            if (!this.get("effective_readonly")) {
                self._updating_editor = false;
                this.$textarea = this.$el.find('textarea');
                var width = ((this.node.attrs || {}).editor_width || '100%');
                var height = ((this.node.attrs || {}).editor_height || 250);
                this.$textarea.cleditor({
                    width: width, // width not including margins, borders or padding
                    height: height, // height not including margins, borders or padding
                    controls:   // controls to add to the toolbar
                        "bold italic underline strikethrough | font size " +
                            " style " +
                            "| color highlight removeformat | bullets numbering | outdent " +
                            "indent |  alignleft center alignright justify | undo redo | link unlink | fileuploader imageuploader videouploader icon | source",
                    //"bold italic underline strikethrough " +
                    //"| removeformat | bullets numbering | outdent " +
                    //"indent | link unlink | fileuploader imageuploader icon | source",
                    bodyStyle:  // style to assign to document body contained within the editor
                        "margin:4px; color:#4c4c4c; font-size:13px; font-family:\"Lucida Grande\",Helvetica,Verdana,Arial,sans-serif; cursor:text"
                });
                this.$cleditor = this.$textarea.cleditor()[0];
                this.$cleditor.change(function () {
                    if (!self._updating_editor) {
                        self.$cleditor.updateTextArea();
                        self.internal_set_value(self.$textarea.val());
                    }
                });
            }
        }
    });

    instance.web.form.FieldMany2ManyBinaryMultiFiles = instance.web.form.AbstractField.extend(instance.web.form.CompletionFieldMixin, instance.web.form.ReinitializeFieldMixin, {
        template: "FieldBinaryFileUploader",
        init: function (field_manager, node) {
            this._super(field_manager, node);
            this.field_manager = field_manager;
            this.node = node;
            if (this.field.type != "many2many" || this.field.relation != 'ir.attachment') {
                throw _.str.sprintf(_t("The type of the field '%s' must be a many2many field with a relation to 'ir.attachment' model."), this.field.string);
            }
            this.ds_file = new instance.web.DataSetSearch(this, 'ir.attachment');
            this.fileupload_id = _.uniqueId('oe_fileupload_temp');
            $(window).on(this.fileupload_id, _.bind(this.on_file_loaded, this));
        },
        initialize_content: function () {
            this.$el.on('change', 'input.oe_form_binary_file', this.on_file_change);
        },
        set_value: function (value_) {
            var value_ = value_ || [];
            var self = this;
            var ids = [];
            _.each(value_, function (command) {
                if (isNaN(command) && command.id == undefined) {
                    switch (command[0]) {
                        case commands.CREATE:
                            ids = ids.concat(command[2]);
                            return;
                        case commands.REPLACE_WITH:
                            ids = ids.concat(command[2]);
                            return;
                        case commands.UPDATE:
                            ids = ids.concat(command[2]);
                            return;
                        case commands.LINK_TO:
                            ids = ids.concat(command[1]);
                            return;
                        case commands.DELETE:
                            ids = _.filter(ids, function (id) {
                                return id != command[1];
                            });
                            return;
                        case commands.DELETE_ALL:
                            ids = [];
                            return;
                    }
                } else {
                    ids.push(command);
                }
            });
            this._super(ids);
        },
        get_value: function () {
            return _.map(this.get('value'), function (value) {
                return commands.link_to(isNaN(value) ? value.id : value);
            });
        },
        get_file_url: function (attachment) {
            return this.session.url('/web/binary/saveas', {model: 'ir.attachment', field: 'datas', filename_field: 'datas_fname', id: attachment['id']});
        },
        read_name_values: function () {
            var self = this;
            // select the list of id for a get_name
            var values = [];
            _.each(this.get('value'), function (val) {
                if (typeof val != 'object') {
                    values.push(val);
                }
            });
            // send request for get_name
            if (values.length) {
                return this.ds_file.call('read', [values, ['id', 'name', 'datas_fname']]).done(function (datas) {
                    _.each(datas, function (data) {
                        data.no_unlink = true;
                        data.url = self.session.url('/web/binary/saveas', {model: 'ir.attachment', field: 'datas', filename_field: 'datas_fname', id: data.id});

                        _.each(self.get('value'), function (val, key) {
                            if (val == data.id) {
                                self.get('value')[key] = data;
                            }
                        });
                    });
                });
            } else {
                return $.when(this.get('value'));
            }
        },
        render_value: function () {
            var self = this;
            this.read_name_values().then(function (datas) {

                var render = $(instance.web.qweb.render('FieldBinaryFileUploader.files', {'widget': self}));
                render.on('click', '.oe_delete', _.bind(self.on_file_delete, self));
                self.$('.oe_placeholder_files, .oe_attachments').replaceWith(render);

                // reinit input type file
                var $input = self.$('input.oe_form_binary_file');
                $input.after($input.clone(true)).remove();
                self.$(".oe_fileupload").show();

            });
        },
        on_file_change: function (event) {
            event.stopPropagation();
            var self = this;
            var $target = $(event.target);
            if ($target.val() !== '') {

                var filename = $target.val().replace(/.*[\\\/]/, '');

                // if the files is currently uploded, don't send again
                if (!isNaN(_.find(this.get('value'), function (file) {
                    return (file.filename || file.name) == filename && file.upload;
                }))) {
                    return false;
                }

                // block UI or not
                if (this.node.attrs.blockui > 0) {
                    instance.web.blockUI();
                }

                // if the files exits for this answer, delete the file before upload
                var files = _.filter(this.get('value'), function (file) {
                    if ((file.filename || file.name) == filename) {
                        self.ds_file.unlink([file.id]);
                        return false;
                    } else {
                        return true;
                    }
                });

                // TODO : unactivate send on wizard and form

                // submit file
                this.$('form.oe_form_binary_form').submit();
                this.$(".oe_fileupload").hide();

                // add file on result
                files.push({
                    'id': 0,
                    'name': filename,
                    'filename': filename,
                    'url': '',
                    'upload': true
                });

                this.set({'value': files});
            }
        },
        on_file_loaded: function (event, result) {
            var files = this.get('value');

            // unblock UI
            if (this.node.attrs.blockui > 0) {
                instance.web.unblockUI();
            }

            // TODO : activate send on wizard and form

            if (result.error || !result.id) {
                this.do_warn(_t('Uploading error'), result.error);
                files = _.filter(files, function (val) {
                    return !val.upload;
                });
            } else {
                for (var i in files) {
                    if (files[i].filename == result.filename && files[i].upload) {
                        files[i] = {
                            'id': result.id,
                            'name': result.name,
                            'filename': result.filename,
                            'url': this.get_file_url(result)
                        };
                    }
                }
            }

            this.set({'value': files});
            this.render_value()
        },
        on_file_delete: function (event) {
            event.stopPropagation();
            var file_id = $(event.target).data("id");
            if (file_id) {
                var files = [];
                for (var i in this.get('value')) {
                    if (file_id != this.get('value')[i].id) {
                        files.push(this.get('value')[i]);
                    }
                    else if (!this.get('value')[i].no_unlink) {
                        this.ds_file.unlink([file_id]);
                    }
                }
                this.set({'value': files});
            }
        }
    });


};