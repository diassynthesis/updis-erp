# -*- coding: utf-8 -*-
import logging
import simplejson
import base64
import tools
import os
import openerp
import time

from openerp.addons.web.controllers.main import manifest_list, module_boot,html_template

class InternalHome(openerp.addons.web.http.Controller):
	_cp_path = "/web/clupload"
	def _create_attachment(self,req,qqfile,resize_image=False):
		context = req.session.eval_context(req.context)
		Model = req.session.model('ir.attachment')

		datas = base64.encodestring(req.httprequest.data)
		if resize_image:
			datas = tools.image_resize_image(datas,size=(700,700))
		attachment_id = Model.create({
			'name': qqfile,
			'datas': datas,
			'datas_fname': qqfile,
		}, context)		
		args = {
			'filename': qqfile,
			'id':  attachment_id,
			'success': True,			
		}
		return args
	@openerp.addons.web.http.httprequest
	def upload_image(self, req, qqfile):		
		try:	
			args = self._create_attachment(req,qqfile,True)		
			# model, id, field, **kw
			url = '%s/web/binary/image?session_id=%s&model=ir.attachment&field=datas&id=%s'%(req.httprequest.url_root, req.session_id, args['id'])
			args['url'] = url
		except Exception, e:
			args = { 'error': e.message}
		return req.make_response(simplejson.dumps(args))
	@openerp.addons.web.http.httprequest
	def upload_file(self, req, qqfile):
		try:	
			args = self._create_attachment(req,qqfile)		
			# model, field, id=None, filename_field=None, **kw)
			url = '%s/web/binary/saveas?session_id=%s&model=ir.attachment&field=datas&filename_field=datas_fname&id=%s'%(req.httprequest.url_root, req.session_id, args['id'])
			args['url'] = url
		except Exception, e:
			args = { 'error': e.message}
		return req.make_response(simplejson.dumps(args))