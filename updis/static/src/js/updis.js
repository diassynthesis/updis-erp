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
			self.$el.appendTo($("#header"));
		}
	});
	openerp.web.client_actions.add("internal_home","openerp.web.Head");

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
			pagies.query(["name","write_date"]).filter([['parent_id','=','通知']]).all().then(function(res){				
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
					views: [['view_wiki_form','form']],
					target:'current',
					// pager : false,
					// search_view: false,
					action_buttons: false
					// sidebar:false
				}
				self.getParent().action_manager.do_action(options);
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
	openerp.web.NewsItem = openerp.web.Widget.extend({
		template:'InternalHome.newsitem',
		init:function(parent,news_id){
			this._super(parent);
			this.newsId=news_id;
		},
		start:function(){
			var self=this;
			var Page = new openerp.web.Model("document.page");
			Page.query(["name","display_content","write_date"]).filter([["id",'=',this.newsId]]).first().then(function(res){
				self.on_news_item_loaded(res);
			});
		},
		on_news_item_loaded:function(item){
			var self=this;
			self.newsitem=item;
			self.renderElement();
			self.trigger("news_item_loaded");
			self.$el.on("click","a#back",function(ev){
				ev.preventDefault();
				self.trigger("load_list_page");
			});
		}
	});
	openerp.web.Foot = openerp.web.Widget.extend({
		template:"InternalHome.foot"
	});
	openerp.web.InternalHome = openerp.web.Client.extend({
		_template:'InternalHome',	
		init: function(){
        	this._super.apply(this, arguments);
		},
		start:function(){
			var self = this;
        	return $.when(this._super()).pipe(function() {
        		self.session.session_authenticate('demo', 'admin', 'admin').pipe(function(){	        		
	        		self.action_manager.do_action("internal_home");
	        		self.show_shortcuts();
	        		self.show_news();
	        		self.show_content();
	        		self.show_foot();
        		});
        	});			
		},
		show_shortcuts:function(){
			var self= this;	
			self.shortcuts = new openerp.web.Shortcuts(self);
			self.shortcuts.appendTo(self.$("#shortcuts"));			
		},
		show_news:function(){
			var self= this;	
			self.news = new openerp.web.News(self);
			self.news.appendTo(self.$("#bodyContent"));		
			self.news.on("read_news_item",self,self.on_read_news_item);	
		},
		show_content:function(){
			var self=this;
			self.content = new openerp.web.Content();
			self.content.appendTo(self.$("#bodyContent"));
		},
		show_foot:function(){
			var self= this;	
			self.foot = new openerp.web.Foot(self);
			self.foot.appendTo(self.$(".footer-holder"));			
		},
		on_read_news_item:function(nid){
			var self = this;
			self.news_item = new openerp.web.NewsItem(self,nid);
			self.news_item.on("news_item_loaded",this,this.on_news_item_loaded);
			self.news_item.on("load_list_page",this,this.on_load_list_page);			
			self.news_item.insertAfter(this.$("#shortcuts"));		
		},
		on_news_item_loaded:function(){
			var self=this;
			self.news.destroy();
			self.content.destroy();
		},
		on_load_list_page:function(){
			var self=this;
			self.news_item.destroy();
			self.show_news();
			self.show_content();
		}
	})
}