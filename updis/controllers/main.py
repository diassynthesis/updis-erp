# -*- coding: utf-8 -*-
import logging
import simplejson
import os
import openerp
import time

from openerp.addons.web.controllers.main import manifest_list, module_boot,html_template

class InternalHome(openerp.addons.web.http.Controller):
	_cp_path = "/cms"
	@openerp.addons.web.http.httprequest
	def app(self,req,**kw):
		js = "\n        ".join('<script type="text/javascript" src="%s"></script>' % i for i in manifest_list(req, None, 'js'))
		js += '\n <script type="text/javascript" src="/updis/static/src/js/updis.js"></script>'
		js += '\n <script type="text/javascript" src="/updis/static/src/js/bootstrap.js"></script>'
		css = "\n        ".join('<link rel="stylesheet" href="%s">' % i for i in manifest_list(req, None, 'css'))
		css += '\n <link rel="stylesheet" href="/updis/static/src/css/bootstrap.css">'
		css += '\n <link rel="stylesheet" href="/updis/static/src/css/common.css">'
		css += '\n <link rel="stylesheet" href="/updis/static/src/css/bootstrap-responsive.css">'
		css += '\n <link rel="stylesheet" href="/updis/static/src/css/internal-home.css">'
		# cookie = req.httprequest.cookies.get("instance0|session_id")
		# session_id = cookie.replace("%22","")
		# template = html_template.replace('<html','<html manifest="/pos/manifest?session_id=%s"'%session_id)
		print js
		r = html_template % {
			'js': js,
			'css': css,
            'modules': simplejson.dumps(module_boot(req)+['updis',]),
			'init': 'var wc = new s.web.InternalHome();wc.appendTo($(document.body));'
		}
		return r