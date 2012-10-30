openerp.updis = function(openerp) {
	var QWeb = openerp.web.qweb;	
	openerp.web.Head = openerp.web.Widget.extend({
		template:"InternalHome.head",
		init:function(){
        	this._super.apply(this, arguments);
		},
		start:function(){
			this._super.apply(this, arguments);
		}
	});
	openerp.web.Service = openerp.web.Widget.extend({
		template:"InternalHome.service"
	});
	openerp.web.News = openerp.web.Widget.extend({
		template:"InternalHome.news",
		
		init:function(){
        	this._super.apply(this, arguments);
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
				self.trigger("read_news_item",news_id);
			});
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
		}
	});
	// openerp.web.Banner = openerp.web.Widget.extend({
	// 	template:"InternalHome.banner"
	// });
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
	        		self.show_head();
	        		// self.show_banner();
	        		self.show_service();
	        		self.show_news();
	        		self.show_foot();
						        	
        		});
        	});			
		},
		show_head:function(){
			var self= this;	
			self.head = new openerp.web.Head(self);
			self.head.appendTo(self.$el);
		},
		show_service:function(){
			var self= this;	
			self.service = new openerp.web.Service(self);
			self.service.appendTo(self.$el);			
		},
		show_news:function(){
			var self= this;	
			self.news = new openerp.web.News(self);
			self.news.appendTo(self.$el);		
			self.news.on("read_news_item",self,self.on_read_news_item);	
		},
		// show_banner:function(){
		// 	var self= this;	
		// 	self.banner = new openerp.web.Banner(self);
		// 	self.banner.appendTo(self.$el);			
		// },
		show_foot:function(){
			var self= this;	
			self.foot = new openerp.web.Foot(self);
			self.foot.appendTo(self.$el);			
		},
		on_read_news_item:function(nid){
			var self = this;
			self.news_item = new openerp.web.NewsItem(self,nid);
			self.news_item.on("news_item_loaded",this,this.on_news_item_loaded);
			self.news_item.insertAfter(this.$("#head"));		
		},
		on_news_item_loaded:function(){
			var self=this;
			self.news.destroy();
			self.banner.destroy();
			self.service.destroy();
		}
	})
}