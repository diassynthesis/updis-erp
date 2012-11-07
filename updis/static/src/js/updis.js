openerp.updis = function(openerp) {
	var QWeb = openerp.web.qweb;	
	openerp.web.AddToInternalHome = openerp.web.search.Input.extend({
		template: 'SearchView.addtointernalhome',
		_in_drawer: true,
		start:function(){
			var self = this;
			this.$el
				.on("click",'h4',this.proxy('show_option'))
				.on("submit","form",function(e){
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
	openerp.web.SearchView.include({
		add_common_inputs:function(){
			this._super();
			(new openerp.web.AddToInternalHome(this));
		}
	});	
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

			// self.$el.appendTo($("#header"));
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
				self.getParent().action_manager.do_action("internal_home");
			})
		}
	});

	openerp.web.Shortcuts = openerp.web.Widget.extend({
		template:"InternalHome.shortcuts"
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

	openerp.web.News = openerp.web.Widget.extend({
		template:"InternalHome.news",
		
		init:function(parent){
        	this._super(parent);
			this.format=openerp.web.format_value;
		},
		start:function(){
			var self = this;
			
			var pagies = new openerp.web.Model("document.page");
			pagies.query(["name","write_date"]).filter([['parent_id','=','本院快讯']]).all().then(function(res){				
				self.kuanxun_news=res;	
				self.on_loaded();			
			});
			pagies.query(["name","write_date"]).filter([['parent_id','=','通知'],['type','=','content']]).all().then(function(res){				
				self.tongzhi_news=res;
				self.on_loaded();
			});
			pagies.query(["name","write_date"]).filter([['parent_id','=','招投标信息']]).all().then(function(res){				
				self.toubiao_news=res;
				self.on_loaded();
			});
		},
		on_loaded:function(){	
			var self = this;
			self.renderElement();		
			self.$el.on("click","a",function(evt){				
				evt.preventDefault();
				var news_id=$(this).data('id');
				var options= {
					type:'ir.actions.act_window',
					res_model: 'document.page',
					res_id: news_id,
					views: [[false,'form']],
					target:'current',
					// pager : false,
					// search_view: false,
					action_buttons: false,
					flags:{
						// 'search_view':false
						'action_buttons':false,
						'display_title':true
					},
					context:{
						'search_default_name':'acd'
					}
					// sidebar:false
				}
				self.do_action(options);
				// self.trigger("read_news_item",news_id);
			});
		}
	});
	openerp.web.Content = openerp.web.Widget.extend({
		template:'InternalHome.content',
		init:function(parent){
			this._super(parent);
		},
		start:function(){

		}
	});
	openerp.web.Foot = openerp.web.Widget.extend({
		template:"InternalHome.foot"
	});
	openerp.web.InternalHomePage = openerp.web.Widget.extend({
		init:function(){
        	this._super.apply(this, arguments);
		},
		start:function(){
			var self = this;
			this._super.apply(this, arguments);			
			// self.$el.appendTo($("#header"));
			self.show_shortcuts();
    		self.show_news();
    		self.show_content();
    		self.$el.appendTo($("#bodyContent"));
		},
		show_shortcuts:function(){
			var self= this;	
			self.shortcuts = new openerp.web.Shortcuts(self);
			self.shortcuts.appendTo(self.$el);			
		},
		show_news:function(){
			var self= this;	
			self.news = new openerp.web.News(self);
			self.news.appendTo(self.$el);		
			// self.news.on("read_news_item",self,self.on_read_news_item);	
		},
		show_content:function(){
			var self=this;
			self.content = new openerp.web.Content();
			self.content.appendTo(self.$el);
		}
	});
	openerp.web.client_actions.add("internal_home","openerp.web.InternalHomePage");
	openerp.web.InternalHome = openerp.web.Client.extend({
		_template:'InternalHome',	
		init: function(){
        	this._super(parent);
		},
		start:function(){
			var self = this;
        	return $.when(this._super()).pipe(function() {
        		self.session.session_authenticate('demo', 'admin', 'admin').pipe(function(){	        			        		
	        		self.show_head();
	        		self.show_internal_common();
	        		self.action_manager.do_action("internal_home");
	        		self.show_foot();
        		});
        	});			
		},
		show_internal_common:function(){
			var self = this;
			self.menu = new openerp.web.InternalHomeMenu(self);
			self.menu.appendTo(self.$('#header'));
        	self.menu.on('menu_click', this, this.on_menu_action);
		},
		show_head:function(){
			var self= this;	
			self.head = new openerp.web.Head(self);
			self.head.appendTo(self.$("#header"));			
		},
		show_foot:function(){
			var self= this;	
			self.foot = new openerp.web.Foot(self);
			self.foot.appendTo(self.$(".footer-holder"));			
		},
		on_menu_action: function(options) {
	        var self = this;
	        return this.rpc("/web/action/load", { action_id: options.action_id })
	            .pipe(function (result) {
	                var action = result;
	                if (options.needaction) {
	                    action.context.search_default_message_unread = true;
	                }
	                return $.when(self.action_manager.do_action(action, {
	                    clear_breadcrumbs: true,
	                    action_menu_id: self.menu.current_menu,
	                })).fail(function() {
	                    self.menu.open_menu(options.previous_menu_id);
	                });
	            });
	    }
	})
}