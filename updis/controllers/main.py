# -*- coding: utf-8 -*-
import logging
import simplejson
import os
import openerp
import time

from openerp.addons.web import nonliterals
from openerp.addons.web.controllers.main import manifest_list, module_boot,html_template

class InternalHomeMenu(openerp.addons.web.http.Controller):
	_cp_path = "/internalhome"
	@openerp.addons.web.http.jsonrequest
	def add_to_home_menu(self, req, parent_menu_id, action_id, context_to_save, domain, view_type, view_mode, name=''):
		to_eval = nonliterals.CompoundContext(context_to_save)
		to_eval.session = req.session
		ctx = dict((k, v) for k, v in to_eval.evaluate().iteritems()
				   if not k.startswith('search_default_'))
		domain = nonliterals.CompoundDomain(domain)
		domain.session = req.session
		domain = domain.evaluate()
		act_window = req.session.model(view_type).copy(action_id,{
			'domain':str(domain),
			'context':str(ctx),
			# 'view_mode':view_mode,
			'name':name
			})
		menu_id = req.session.model("internal.home.menu").create({
			'name':name,
			'parent_id':parent_menu_id,
			'icon': 'STOCK_DIALOG_QUESTION',
			'action': 'ir.actions.act_window,'+ str(act_window),
			})
		return True
class InternalHome(openerp.addons.web.http.Controller):
	_cp_path = "/cms"
	@openerp.addons.web.http.httprequest
	def index(self,req,**kw):
		js = "\n        ".join('<script type="text/javascript" src="%s"></script>' % i for i in manifest_list(req, None, 'js'))
		js += '\n <script type="text/javascript" src="/updis/static/src/js/updis.js"></script>'
		# js += '\n <script type="text/javascript" src="/updis/static/src/js/bootstrap.js"></script>'
		css = "\n        ".join('<link rel="stylesheet" href="%s">' % i for i in manifest_list(req, None, 'css'))
		css += '\n <link rel="stylesheet" href="/updis/static/src/css/style.css">'
		# css += '\n <link rel="stylesheet" href="/updis/static/src/css/common.css">'
		# css += '\n <link rel="stylesheet" href="/updis/static/src/css/ie8.css">'
		css += '\n <link rel="stylesheet" href="/updis/static/src/css/internal-home.css">'
		css += '\n <link rel="stylesheet" href="/updis/static/src/css/karma-teal-grey.css">'
		# css += '\n <link rel="stylesheet" href="/updis/static/src/css/secondary-teal-grey.css">'
		# css += '\n <link rel="stylesheet" href="/updis/static/src/css/bootstrap-responsive.css">'
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