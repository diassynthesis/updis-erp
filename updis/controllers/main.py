# -*- coding: utf-8 -*-
import logging
import operator
import simplejson
import os
import openerp
import time

from openerp.addons.web import nonliterals
from openerp.addons.web.controllers.main import manifest_list, module_boot,html_template

class InternalHomeMenu(openerp.addons.web.http.Controller):
	_cp_path = "/internalhome"
	@openerp.addons.web.http.jsonrequest
	def load_home_page_categories(self,req):
		ret = {}
		context = req.session.eval_context(req.context)
		Page = req.session.model("document.page")	

		# All categories to display on internal home page
		categories_ids = Page.search([['type','=','category'],['display_position','!=',False]])		
		categories = Page.read(categories_ids,['name','display_position','sequence'])
		categories_map = dict((category['id'],category) for category in categories)

		# import pdb;pdb.set_trace()
		for cat in categories:
			ret.setdefault(cat['display_position'],[]).append(cat)
			cat_id = cat['id']
			pagies_id = Page.search([['type','=','content'],['parent_id','=',cat_id]],limit=6)
			pagies = Page.read(pagies_id,['name','write_date','write_uid','sequence'])
			categories_map[cat_id]['children'] = pagies
		for k,v in ret.items():
			v.sort(key=operator.itemgetter('sequence'))
			for cat in v:
				cat.setdefault('children',[]).sort(key=operator.itemgetter('sequence'))

		ret.update(self.do_load_department_pagies(req))
		return ret
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
	@openerp.addons.web.http.jsonrequest
	def load_menu(self,req):
		return {'data':self.do_load_menu(req)}

	def do_get_roots(self,req):
		s = req.session
		context = s.eval_context(req.context)
		Menus = s.model("internal.home.menu")
		return Menus.search([['parent_id','=',False]],0,False,False,context)

	def do_load_menu(self,req):
		""""Loads all internal home menus and their sub menus"""
		context = req.session.eval_context(req.context)
		Menus = req.session.model("internal.home.menu")
		menu_ids = Menus.search([],0,False,False,context)
		menu_items = Menus.read(menu_ids, ['name', 'sequence', 'parent_id', 'action', 'needaction_enabled', 'needaction_counter'], context)
		menu_roots = Menus.read(self.do_get_roots(req),['name', 'sequence', 'parent_id', 'action', 'needaction_enabled', 'needaction_counter'], context)
		menu_root = {'id': False, 'name': 'root', 'parent_id': [-1, ''], 'children' : menu_roots}

		menu_items.extend(menu_roots)
		menu_items_map = dict((menu_item['id'],menu_item) for menu_item in menu_items)				
		for menu_item in menu_items:
			if menu_item['parent_id']:
				parent = menu_item['parent_id'][0]
			else:
				parent = False
			if parent in menu_items_map:
				menu_items_map[parent].setdefault('children',[]).append(menu_item)
		for menu_item in menu_items:
			menu_item.setdefault('children',[]).sort(key=operator.itemgetter('sequence'))
		return menu_root
	def do_load_department_pagies(self,req):
		'''
		return {
			departments:[
				'name':XXX,
				'sequence':X,
				'categories':[
					{
						'name':XXX,
						'sequence':X,
						'pagies':[
							{
								'name':XXX,
								'id':XX
							}
						]
					}
				]
			]
		}
		'''
		ret = {}
		Department = req.session.model("hr.department")
		Page = req.session.model("document.page") 
		departments_ids = Department.search([('deleted','=',False)])
		departments = Department.read(departments_ids,['name','sequence'])
		ret['departments'] = departments
		# import pdb;pdb.set_trace()
		for dep in departments:
			categories_ids = Page.search([('type','=','category'),('display_in_departments','=',dep['id'])])
			categories = Page.read(categories_ids,['name','sequence'])
			dep['categories'] = categories
			for cat in categories:
				pagies_id = Page.search([('type','=','content'),('parent_id','=',cat['id']),('department_id','=',dep['id'])],limit=6)
				pagies = Page.read(pagies_id,['name','sequence'])
				cat['pagies'] = pagies
		return ret
		
class InternalHome(openerp.addons.web.http.Controller):
	_cp_path = "/cms"
	@openerp.addons.web.http.httprequest
	def index(self,req,**kw):
		js = "\n        ".join('<script type="text/javascript" src="%s"></script>' % i for i in manifest_list(req, None, 'js'))

		js += '\n <script type="text/javascript" src="/updis/static/src/js/updis.js"></script>'
		js += '\n <script type="text/javascript" src="/updis/static/src/js/karma.js"></script>'
		js += '\n <script type="text/javascript" src="/updis/static/src/js/tab.js"></script>'
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