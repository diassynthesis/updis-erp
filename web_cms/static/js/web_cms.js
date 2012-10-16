//  @@@ web_cms custom JS @@@

openerp.web_cms = function(openerp) {
    // extend openerp here
    openerp.webclient.on_logout.add_first(function(){
    	alert("Log out");
    });
};
