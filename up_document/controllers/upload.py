import base64
import xmlrpclib
import simplejson
from xmlrpclib import Fault
from openerp.osv import osv
from web_clupload.controllers.main import InternalHome
from openerp.addons.web.controllers.main import Binary, openerpweb, content_disposition
import openerp
from  openerp.tools.translate import _

__author__ = 'cysnake4713'


class InternalHomeExtend(InternalHome):
    @openerp.addons.web.http.httprequest
    def multi_upload(self, req, qqfile, parent_id, res_id=0, res_model=None):
        attachment_obj = req.session.model('ir.attachment')
        try:
            attachment_id = attachment_obj.create(
                {
                    'name': qqfile.filename,
                    'datas': qqfile,
                    'datas_fname': qqfile.filename,
                    'parent_id': int(parent_id),
                    'res_model': res_model,
                    'res_id': int(res_id),
                }, context=req.context)
            args = {'files': [{"name": qqfile.filename,
                               "size": 0,
                               "url": "",
                               "thumbnailUrl": "",
                               "deleteUrl": "",
                               "deleteType": "DELETE", }]}
        except Fault, e:
            args = {"files": [{"name": qqfile.filename,
                               "size": 0,
                               "error": e.faultCode}]}
        except Exception, e:
            args = {"files": [{"name": qqfile.filename,
                               "size": 0,
                               "error": e.message}]}
        return req.make_response(simplejson.dumps(args))


class BinaryExtend(Binary):

    def attachment_saveas(self, req, model, field, id=None, filename_field=None, **kw):
        Model = req.session.model(model)
        fields = ['datas']
        if filename_field:
            fields.append(filename_field)
        if id:
            res = Model.read([int(id)], fields, req.context)[0]
        else:
            res = Model.default_get(fields, req.context)
        file_out = res.get('datas', '')
        if not file_out:
            return req.not_found()
        else:
            filename = '%s_%s' % (model.replace('.', '_'), id)
            if filename_field:
                filename = res.get(filename_field, '') or filename
            return req.make_response(file_out,
                                     [('Content-Type', 'application/octet-stream'),
                                      ('Content-Disposition', content_disposition(filename, req))])

    @openerpweb.httprequest
    def saveas(self, req, model, field, id=None, filename_field=None, **kw):
        if model == 'ir.attachment':
            attachment_obj = req.session.model(model)
            download_able = attachment_obj.check_downloadable([int(id)], req.context)
            if download_able == 3:
                attachment_obj.log_info([int(id)], _('download this file'), context=req.context)
                return self.attachment_saveas(req, model, field, id, filename_field, **kw)
            else:
                if download_able == 1:
                    args = {'error': {'message': _('You apply download request but not approve yet! Please be patient'),
                                      'data': {'debug': ''}}}
                else:
                    args = {'error': {'message': _('You have no privilege to download some of the attachments'),
                                      'data': {'debug': ''}}}

                return req.make_response(simplejson.dumps(args))
        else:
            return super(BinaryExtend, self).saveas(req, model, field, id, filename_field, **kw)

    def save_as_attachment_ajax(self, req, data, token):
        jdata = simplejson.loads(data)
        model = jdata['model']
        field = jdata['field']
        data = None
        id = jdata.get('id', None)
        filename_field = jdata.get('filename_field', None)
        context = jdata.get('context', {})

        Model = req.session.model(model)
        fields = [field]
        if filename_field:
            fields.append(filename_field)
        if data:
            res = {field: data}
        elif id:
            res = Model.read([int(id)], fields, context)[0]
        else:
            res = Model.default_get(fields, context)
        file_out = res.get(field, '')
        if not file_out:
            raise ValueError(_("No content found for field '%s' on '%s:%s'") %
                             (field, model, id))
        else:
            filename = '%s_%s' % (model.replace('.', '_'), id)
            if filename_field:
                filename = res.get(filename_field, '') or filename
            return req.make_response(file_out,
                                     headers=[('Content-Type', 'application/octet-stream'),
                                              ('Content-Disposition', content_disposition(filename, req))],
                                     cookies={'fileToken': token})

    @openerpweb.httprequest
    def saveas_ajax(self, req, data, token):
        jdata = simplejson.loads(data)
        model = jdata['model']
        attachment_id = jdata.get('id', None)
        if model == 'ir.attachment':
            attachment_obj = req.session.model(model)
            download_able = attachment_obj.check_downloadable([int(attachment_id)], req.context)
            if download_able == 3:
                attachment_obj.log_info([int(attachment_id)], _('download this file'), context=req.context)
                return self.save_as_attachment_ajax(req, data, token)
            else:
                if download_able == 1:
                    args = {'message': _(
                        'You have no privilege to download some of the attachments, Please apply download request.'),
                            'data': {}, }
                else:
                    args = {'message': _('You have no privilege to download some of the attachments'), 'data': {}, }
                return req.make_response(simplejson.dumps(args))
        else:
            return super(BinaryExtend, self).saveas_ajax(req, data, token)
