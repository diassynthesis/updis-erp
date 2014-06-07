/**
 * Created by cysnake4713 on 13-10-23.
 */
openerp.up_web = function (instance) {

    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    /*
     # Values: (0, 0,  { fields })    create
     #         (1, ID, { fields })    update
     #         (2, ID)                remove (delete)
     #         (3, ID)                unlink one (target id or target of relation)
     #         (4, ID)                link
     #         (5)                    unlink all (only valid for one2many)
     */
    var commands = {
        // (0, _, {values})
        CREATE: 0,
        'create': function (values) {
            return [commands.CREATE, false, values];
        },
        // (1, id, {values})
        UPDATE: 1,
        'update': function (id, values) {
            return [commands.UPDATE, id, values];
        },
        // (2, id[, _])
        DELETE: 2,
        'delete': function (id) {
            return [commands.DELETE, id, false];
        },
        // (3, id[, _]) removes relation, but not linked record itself
        FORGET: 3,
        'forget': function (id) {
            return [commands.FORGET, id, false];
        },
        // (4, id[, _])
        LINK_TO: 4,
        'link_to': function (id) {
            return [commands.LINK_TO, id, false];
        },
        // (5[, _[, _]])
        DELETE_ALL: 5,
        'delete_all': function () {
            return [5, false, false];
        },
        // (6, _, ids) replaces all linked records with provided ids
        REPLACE_WITH: 6,
        'replace_with': function (ids) {
            return [6, false, ids];
        }
    };


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
                        "margin:4px; color:#4c4c4c; font-size:13px; font-family:'Lucida Grande',Helvetica,Verdana,Arial,sans-serif; cursor:text"
                });
                this.$cleditor = this.$textarea.cleditor()[0];
                this.$cleditor.change(function () {
                    if (!self._updating_editor) {
                        self.$cleditor.updateTextArea();
                        self.internal_set_value(self.$textarea.val());
                    }
                });
                if (this.field.translate) {
                    var $img = $('<img class="oe_field_translate oe_input_icon" src="/web/static/src/img/icons/terp-translate.png" width="16" height="16" border="0"/>')
                        .click(this.on_translate);
                    this.$cleditor.$toolbar.append($img);
                }
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
            self.res_context = self.node.attrs.context ? self.node.attrs.context : "{}";
            self.res_model = self.node.attrs.res_model ? self.node.attrs.res_model : self.view.model;
            if (typeof self.node.attrs.res_id == "string") {
                var index_name = self.node.attrs.res_id;
                self.res_id = self.view.fields[index_name].get_value();
            } else {
                self.res_id = 0
            }

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
                this.do_warn(_t('Uploading Error'), result.error);
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

    instance.web.form.FieldMany2One.include({
        render_editable: function () {
            var self = this;
            this.$input = this.$el.find("input");

            this.init_error_displayer();

            self.$input.on('focus', function () {
                self.hide_error_displayer();
            });

            this.$drop_down = this.$el.find(".oe_m2o_drop_down_button");
            this.$follow_button = $(".oe_m2o_cm_button", this.$el);

            this.$follow_button.click(function (ev) {
                ev.preventDefault();
                if (!self.get('value')) {
                    self.focus();
                    return;
                }
                var pop = new instance.web.form.FormOpenPopup(self);
                pop.show_element(
                    self.field.relation,
                    self.get("value"),
                    self.build_context(),
                    {
                        title: _t("Open: ") + self.string
                    }
                );
                pop.on('write_completed', self, function () {
                    self.display_value = {};
                    self.render_value();
                    self.focus();
                    self.view.do_onchange(self);
                });
            });

            // some behavior for input
            var input_changed = function () {
                if (self.current_display !== self.$input.val()) {
                    self.current_display = self.$input.val();
                    if (self.$input.val() === "") {
                        self.internal_set_value(false);
                        self.floating = false;
                    } else {
                        self.floating = true;
                    }
                }
            };
            this.$input.keydown(input_changed);
            this.$input.change(input_changed);
            this.$drop_down.click(function () {
                if (self.$input.autocomplete("widget").is(":visible")) {
                    self.$input.autocomplete("close");
                    self.$input.focus();
                } else {
                    if (self.get("value") && !self.floating) {
                        self.$input.autocomplete("search", "");
                    } else {
                        self.$input.autocomplete("search");
                    }
                }
            });

            // Autocomplete close on dialog content scroll
            var close_autocomplete = _.debounce(function () {
                if (self.$input.autocomplete("widget").is(":visible")) {
                    self.$input.autocomplete("close");
                }
            }, 50);
            this.$input.closest(".ui-dialog .ui-dialog-content").on('scroll', this, close_autocomplete);

            self.ed_def = $.Deferred();
            self.uned_def = $.Deferred();
            var ed_delay = 200;
            var ed_duration = 15000;
            var anyoneLoosesFocus = function (e) {
                var used = false;
                if (self.floating) {
                    if (self.last_search.length > 0) {
                        if (self.last_search[0][0] != self.get("value")) {
                            self.display_value = {};
                            self.display_value["" + self.last_search[0][0]] = self.last_search[0][1];
                            self.reinit_value(self.last_search[0][0]);
                        } else {
                            used = true;
                            self.render_value();
                        }
                    } else {
                        used = true;
                        self.reinit_value(false);
                    }
                    self.floating = false;
                }
                if (used && self.get("value") === false && !self.no_ed) {
                    self.ed_def.reject();
                    self.uned_def.reject();
                    self.ed_def = $.Deferred();
                    self.ed_def.done(function () {
                        self.show_error_displayer();
                        ignore_blur = false;
                        self.trigger('focused');
                    });
                    ignore_blur = true;
                    setTimeout(function () {
                        self.ed_def.resolve();
                        self.uned_def.reject();
                        self.uned_def = $.Deferred();
                        self.uned_def.done(function () {
                            self.hide_error_displayer();
                        });
                        setTimeout(function () {
                            self.uned_def.resolve();
                        }, ed_duration);
                    }, ed_delay);
                } else {
                    self.no_ed = false;
                    self.ed_def.reject();
                }
            };
            var ignore_blur = false;
            this.$input.on({
                focusout: anyoneLoosesFocus,
                focus: function () {
                    self.trigger('focused');
                },
                autocompleteopen: function () {
                    ignore_blur = true;
                },
                autocompleteclose: function () {
                    ignore_blur = false;
                },
                blur: function () {
                    // autocomplete open
                    if (ignore_blur) {
                        return;
                    }
                    if (_(self.getChildren()).any(function (child) {
                        return child instanceof instance.web.form.AbstractFormPopup;
                    })) {
                        return;
                    }
                    self.trigger('blurred');
                }
            });

            var isSelecting = false;
            // autocomplete
            this.$input.autocomplete({
                source: function (req, resp) {
                    self.get_search_result(req.term).done(function (result) {
                        resp(result);
                    });
                },
                select: function (event, ui) {
                    isSelecting = true;
                    var item = ui.item;
                    if (item.id) {
                        self.display_value = {};
                        self.display_value["" + item.id] = item.name;
                        self.reinit_value(item.id);
                    } else if (item.action) {
                        item.action();
                        // Cancel widget blurring, to avoid form blur event
                        self.trigger('focused');
                        return false;
                    }
                },
                focus: function (e, ui) {
                    e.preventDefault();
                },
                html: true,
                // disabled to solve a bug, but may cause others
                //close: anyoneLoosesFocus,
                minLength: 0,
                delay: 0
            });
            //set position for list of suggetions box
            this.$input.autocomplete("option", "position", { my: "left top", at: "left bottom" });
            this.$input.autocomplete("widget").openerpClass();
            // used to correct a bug when selecting an element by pushing 'enter' in an editable list
            this.$input.keyup(function (e) {
                if (e.which === 13) { // ENTER
                    if (isSelecting)
                        e.stopPropagation();
                }
                isSelecting = false;
            });
            this.setupFocus(this.$follow_button);
        }
    });


    instance.web.form.FieldMany2ManyTags.include({
        _search_create_popup: function (view, ids, context) {
            var self = this;
            var pop = new instance.web.form.SelectCreatePopup(this);
            pop.select_element(
                self.field.relation,
                {
                    title: (view === 'search' ? _t("Search: ") : _t("Create: ")) + this.string,
                    initial_ids: ids ? _.map(ids, function (x) {
                        return x[0]
                    }) : undefined,
                    initial_view: view,
                    disable_multiple_selection: false
                },
                self.build_domain(),
                new instance.web.CompoundContext(self.build_context(), context || {})
            );
            pop.on("elements_selected", self, function (element_ids) {
                _.each(element_ids, function (element_id) {
                    self.add_id(element_id);
                });
                self.focus();
            });
        }
    });

    instance.web.ListView.include({
        setup_events: function () {
            var self = this;
            _.each(this.editor.form.fields, function (field, field_name) {
                var setting = false;
                var set_invisible = function () {
                    if (!setting && field.get("effective_readonly")) {
                        setting = true;
                        field.set({invisible: true});
                        setting = false;
                    }
                };
                field.on("change:effective_readonly", self, set_invisible);
                field.on("change:invisible", self, set_invisible);
                set_invisible();
                field.on('change:invisible', self, function () {
                    if (field.get('invisible')) {
                        return;
                    }
                    var item = _(self.fields_for_resize).find(function (item) {
                        return item.field === field;
                    });
                    if (item) {
                        self.resize_field(item.field, item.cell);
                    }
                });
            });

            this.editor.$el.on('keyup keydown', function (e) {
                if (!self.editor.is_editing()) {
                    return true;
                }
                var key = _($.ui.keyCode).chain()
                    .map(function (v, k) {
                        return {name: k, code: v};
                    })
                    .find(function (o) {
                        return o.code === e.which;
                    })
                    .value();
                if (!key) {
                    return true;
                }
                var method = e.type + '_' + key.name;
                if (!(method in self)) {
                    return true;
                }
                return self[method](e);
            });
        }
    })
};