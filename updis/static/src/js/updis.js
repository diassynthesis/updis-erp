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
			this.format=openerp.web.format_value;
		},
		start:function(){
			var self = this;
			var categories = new openerp.web.Model("document.page");
			categories.query(["name","write_date"]).filter([['parent_id','=','本院快讯']]).all().then(function(res){
				// _.each(res,function(itm,idx){
				// 	itm['write_date_relative'] = $.timeago(itm.write_date);
				// });
				self.kuanxun_news=res;
				self.renderElement();
			});
		}
	});
	openerp.web.Banner = openerp.web.Widget.extend({
		template:"InternalHome.banner"
	});
	openerp.web.Foot = openerp.web.Widget.extend({
		template:"InternalHome.foot"
	});
	openerp.web.InternalHome = openerp.web.Client.extend({
		_template:'InternalHome',		
		start:function(){
			var self = this;
        	return $.when(this._super()).pipe(function() {
        		self.session.session_authenticate('demo', 'admin', 'admin').pipe(function(){
	        		self.show_head();
	        		self.show_banner();
	        		self.show_service();
	        		self.show_news();
	        		self.show_foot();
        		});
        	});			
		},
		show_head:function(){
			var self= this;	
			var head = new openerp.web.Head(self);
			head.appendTo(self.$el);
		},
		show_service:function(){
			var self= this;	
			var head = new openerp.web.Service(self);
			head.appendTo(self.$el);			
		},
		show_news:function(){
			var self= this;	
			var head = new openerp.web.News(self);
			head.appendTo(self.$el);			
		},
		show_banner:function(){
			var self= this;	
			var head = new openerp.web.Banner(self);
			head.appendTo(self.$el);			
		},
		show_foot:function(){
			var self= this;	
			var head = new openerp.web.Foot(self);
			head.appendTo(self.$el);			
		}
	})
	openerp.web.WebClient.include({
		
	});
	
}