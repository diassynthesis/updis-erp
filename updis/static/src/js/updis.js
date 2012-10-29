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
				alert($(this).data('id'));
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