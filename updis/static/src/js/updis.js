openerp.updis = function(openerp) {
	var QWeb = openerp.web.qweb;	
	openerp.mail.ThreadMessage.include({
		init: function (parent, datasets, options) {            
            this.is_anonymous = datasets.is_anonymous;
            return this._super(parent,datasets, options);
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
	openerp.web.AddToInternalHome = openerp.web.search.Input.extend({
		template: 'SearchView.addtointernalhome',
		_in_drawer: true,
		start:function(){
			var self = this;
			this.$el .on("click",'h4',this.proxy('show_option')) .on("submit","form",function(e){
				e.preventDefault();
				self.add_internalhome();
			});
			return this.load_data().then(this.proxy("render_data"));
		},
		add_internalhome:function(){
			var self = this;
			var getParent = this.getParent();
			var view_parent = this.getParent().getParent();
			if (! view_parent.action || ! this.$el.find("select").val()) {
				this.do_warn("Can't find dashboard action");
				return;
			}
			var data = getParent.build_search_data();
			var context = new openerp.web.CompoundContext(getParent.dataset.get_context() || []);
			var domain = new openerp.web.CompoundDomain(getParent.dataset.get_domain() || []);
			_.each(data.contexts, context.add, context);
			_.each(data.domains, domain.add, domain);
			this.rpc('/internalhome/add_to_home_menu',{
				parent_menu_id:this.$el.find('select').val(),
				action_id: view_parent.action.id,
				context_to_save:context,
				domain: domain,
				view_type: view_parent.action.type,
				view_mode: view_parent.active_view,
				name:this.$el.find("input").val()
			}).then(function(rs){
				if (r === false) {
					self.do_warn("Could not add to internal home menu");
				} else {
					self.$el.toggleClass('oe_opened');
					self.do_notify("Filter added to dashboard",'');
				}
			})
		},
		render_data:function(res){
			var selection = QWeb.render("SearchView.addtointernalhome.selection",{
				selections:res
			});
			this.$("input").before(selection);
		},
		load_data:function(){
			var internalmenu = new openerp.web.Model("internal.home.menu");
			return internalmenu.query(['name'])
				.all();
		},
		show_option:function(){
			this.$el.toggleClass('oe_opened');			
		}
	});
	// openerp.web.SearchView.include({
	// 	add_common_inputs:function(){
	// 		this._super();
	// 		(new openerp.web.AddToInternalHome(this));
	// 	}
	// });	
	openerp.web.Head = openerp.web.Widget.extend({
		template:"InternalHome.head",
		init:function(parent){
			this._super(parent);
		},
		start:function(){
			var self = this;
			this._super.apply(this, arguments);			
			var pagies = new openerp.web.Model("internal.home.menu");
			pagies.query(["name",'action']).filter([['parent_id','=','Top menu']]).all().then(function(res){				
				self.top_menu_items=res;	
				self.on_loaded();
			});
		},
		on_loaded:function(){
			var self=this;
			self.renderElement();
			self.$el.on("click","a.top-menu",function(evt){				
				evt.preventDefault();				
				var action = $(this).data("action");
				self.getParent().action_manager.do_action(action.split(',')[1]);
			});
			self.$el.on("click","a#company-logo",function(ev){
				ev.preventDefault();
				self.getParent().action_manager.do_action("internal_home",{
					clear_breadcrumbs:true
				});
			});
		}
	});

	openerp.web.InternalHomeMenu = openerp.web.Widget.extend({
		template:'InternalHomeMenu',
		init:function(){

			this._super.apply(this,arguments);
			this.has_been_loaded = $.Deferred();
			this.data={data:{children:[]}};			
		},
		start:function(){
			this._super.apply(this,arguments);
			return this.do_reload();			
		},
		do_reload:function(){
			var self = this;
			return this.rpc("/internalhome/load_menu",{}).then(function(r){
				self.menu_loaded(r);
			});
		},
		menu_loaded:function(data){
			var self = this;
			this.data = data;
			var top_menu_item = data.data.children[0];
			var top_menu = QWeb.render("InternalHomeMenu.head",{rootmenu:top_menu_item});
			$("#menu-main-nav").append(top_menu);

			var mainNav=$('#menu-main-nav');
			var lis=mainNav.find('li');
			var shownav=$("#menu-main-nav");
			lis.children('ul').wrap('<div class="c" / >');
			var cElems=$('.c');
			cElems.wrap('<div class="drop" / >');
			cElems.before('<div class="t"></div>');
			cElems.after('<div class="b"></div>');
			$(shownav).find(".sub-menu").css({display:"block"});
			initNav();

			var footer_menu = data.data.children[2];
			var footer_menu_html = QWeb.render("InternalHomeMenu.footer",{rootmenu:footer_menu});
			$(".footer-holder").html(footer_menu_html);
			this.trigger('internalhomemenu_loaded', data);

			$('a[data-menu]').click(this.on_menu_click);

			this.has_been_loaded.resolve();			
		},
		menu_click:function(id,needaction){
			if (!id) { return; }

			// find back the menuitem in dom to get the action
			var $item = $('a[data-menu=' + id + ']');

			var action_id = $item.data('action-id');	        
			if (action_id) {
				this.trigger('menu_click', {
					action_id: action_id,
					needaction: needaction,
					id: id,
					previous_menu_id: this.current_menu // Here we don't know if action will fail (in which case we have to revert menu)
				}, $item);
			}
			// this.open_menu(id);
		},
		on_menu_click:function(ev){
			ev.preventDefault();
			var needaction = $(ev.target).is('div.oe_menu_counter');
			this.menu_click($(ev.currentTarget).data('menu'), needaction);
		}
	});
	openerp.web.InternalHomePageAction = openerp.web.Widget.extend({		
		init:function(){
			this._super.apply(this, arguments);
			this.data = {data:{children:[]}};
			this.format = openerp.web.format_value;
		},
		start:function(){
			var self = this;
			this._super.apply(this, arguments);
			return this.rpc("/internalhome/load_home_page_categories",{}).then(function(r){
				self.render_data(r);
			});
		},
		render_data:function(data){
			var self = this;
			this.data = data;
			this.shortcut_html = $(QWeb.render("InternalHome.homepage.categories.shortcut",{widget:this}));
			this.shortcut_html.appendTo(self.$el);
			this.content_html = $(QWeb.render("InternalHome.homepage.categories.content",{widget:this}));
			this.content_html.appendTo(self.$el);	
			this.departments_html = $(QWeb.render("InternalHome.homepage.departments",{widget:this}));
			this.departments_html.appendTo(self.$el);

			$.jqtab("#tabs","#tab_conbox","click");	
			$.jqtab("#tabs2","#tab_conbox2","click");			
			$.jqtab("#tabs3","#tab_conbox3","click");

			$(".tabs-container .arrow").click(function(e){
				e.preventDefault();
				var content = $(".tabs-container .tabs");
				var pos = content.position().left + 500;
				if (pos>0) {
					pos=0;
				}
				content.animate({ left: pos }, 1000);
			});
			$(".tabs-container .arrow_r").click(function(ev){
				ev.preventDefault();
				var width = 0;
				$(".tabs-container ul.tabs > li").each(function(idx,itm){width += $(itm).width();});
				var tab_window_width = $(".tabs-container").width();
				var content = $(".tabs-container ul.tabs");				
				var pos = content.position().left - 500;

				if (width + pos < tab_window_width) {
					pos = -width + tab_window_width;
				}
				content.animate({ left: pos }, 1000);
			});
			// $("a.page-item").click(function(ev){
			// 	ev.preventDefault();
			// 	// alert("OK");
			// 	// self.hide();
			// 	var page_id = $(this).data("id");
			// 	self.rpc("/web/action/load", { action_id: "document_page.action_page" }).done(function(result) {
			//               result.res_id = page_id;	                
			//               var tmp = result.views[0];
			//               result.views = [result.views[1]];
			//               self.getParent().do_action(result);
			//           });
			// 	// self.getParent().do_action('document_page.action_page')
			// });
		},
		destroy:function(){
			this.shortcut_html.remove();
			this.content_html.remove();
			this.departments_html.remove();
		}
	});
	openerp.web.client_actions.add("internal_home","openerp.web.InternalHomePageAction");
	openerp.web.InternalHome = openerp.web.WebClient.extend({
		_template:'InternalHome',	
		init: function(){
			this._super(parent);
		},
		show_application:function(){
			var self = this;
			self.show_head();
			self.show_internal_common();
			self.user_menu = new openerp.web.UserMenu(self);
			self.user_menu.appendTo(this.$el.find('.sub-nav2'));
			self.user_menu.on('user_logout', self, self.on_logout);
			self.user_menu.do_update();
			self.bind_hashchange();
			// self.action_manager.do_action("internal_home");
			self.set_title();

			self.$el.find("#link_home").click(function(){				
				self.action_manager.do_action('home');
			})
		},
		bind_hashchange: function() {
			var self = this;
			$(window).bind('hashchange', this.on_hashchange);

			var state = $.bbq.getState(true);
			if (_.isEmpty(state) || state.action == "login") {
				self.action_manager.do_action("internal_home");
			} else {
				$(window).trigger('hashchange');
			}
		},
		show_internal_common:function(){
			var self = this;
			self.menu = new openerp.web.InternalHomeMenu(self);
			self.menu.appendTo(self.$el.find('#header'));
			self.menu.on('menu_click', this, this.on_menu_action);
		},
		show_head:function(){
			var self= this;	
			self.head = new openerp.web.Head(self);
			self.head.appendTo(self.$el.find("#header"));			
		},
		set_title: function(title) {
			title = _.str.clean(title);
			var sep = _.isEmpty(title) ? '' : ' - ';
			document.title = title + sep + 'UPDIS';
		}
	})
}
