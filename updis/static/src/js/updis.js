openerp.updis = function(openerp) {
	var QWeb = openerp.web.qweb;	
	openerp.web.Head = openerp.web.Widget.extend({
		template:"InternalHome.head",
		init:function(){
        	this._super.apply(this, arguments);
		},
		start:function(){
			var self = this;
			this._super.apply(this, arguments);			
			// self.$el.appendTo($("#header"));
		}
	});

	openerp.web.Shortcuts = openerp.web.Widget.extend({
		template:"InternalHome.shortcuts"
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
					action_buttons: false
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
        	this._super.apply(this, arguments);
		},
		start:function(){
			var self = this;
        	return $.when(this._super()).pipe(function() {
        		self.session.session_authenticate('demo', 'admin', 'admin').pipe(function(){	        			        		
	        		self.show_head();
	        		self.action_manager.do_action("internal_home");
	        		self.show_foot();
        		});
        	});			
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
		}
	})
}