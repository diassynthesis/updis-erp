//  @@@ web_cms custom JS @@@

openerp.web_cms = function(openerp) {
	var QWeb = openerp.web.qweb;
    // extend openerp here
    openerp.web.Header.include({
    	do_update:function(){
    		this._super();
    	},
    	on_preferences:function(){
    		console.info("OK");
    		this._super();
    	}
    });
    openerp.web.WebClient.include({
    	show_login: function() {
        	var self = this;		
    		alert("start");
    		this._super(this,arguments);
        },
        set_title: function(title) {
	        title = _.str.clean(title);
	        var sep = _.isEmpty(title) ? '' : ' - ';
	        document.title = title + sep + 'UPDIS';
	    },
    	show_application:function(){
    		console.info("Show show_application");
    		this._super(this,arguments);
    	},
    	show_login:function(){    		
    		alert("Show Login");
    		this._super(this,arguments);
    	}
    });
    openerp.web.Login.include({
    	do_login: function() {
    		alert("OK");
    	}
    });
    openerp.web.Menu.include({
    	// on_loaded:function(data){
    	// 	console.info('Menu loaded');
    		
	    //     this.data = data;
	    //     this.$element.html(QWeb.render("MyMenu", { widget : this }));
	    //     this.$secondary_menu.html(QWeb.render("Menu.secondary", { widget : this }));
	    //     this.$element.add(this.$secondary_menu).find("a").click(this.on_menu_click);
	    //     this.$secondary_menu.find('.oe_toggle_secondary_menu').click(this.on_toggle_fold);
    	// }
    })
};
