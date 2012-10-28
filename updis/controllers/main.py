import openerp

class InternalHome(openerp.addons.web.http.Controller):
	_cp_path = "/home"
	@openerp.addons.web.http.httprequest
	def home(self,req,**kw):
		return html