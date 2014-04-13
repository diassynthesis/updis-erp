import base64
import simplejson
from xmlrpclib import Fault
from web_clupload.controllers.main import InternalHome
from openerp.addons.web.controllers.main import Binary, openerpweb
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
                    'name': qqfile,
                    'datas': base64.encodestring(req.httprequest.data),
                    'datas_fname': qqfile,
                    'parent_id': int(parent_id),
                    'res_model': res_model,
                    'res_id': int(res_id),
                })
            args = {
                'url': '',
                'filename': qqfile,
                'id': attachment_id,
                'success': True,
            }
        # try:
        #     Model = req.session.model('ir.attachment')
        #     args = self._create_attachment(req, qqfile, path="/mp4")
        #     # model, field, id=None, filename_field=None, **kw)
        #     url = 'http://file.updis.cn:81/mp4/%s' % (args['filename'])
        #     args['url'] = url
        #     args['id'] = 'v' + args['filename'].split(".")[0][18:25]
        #     args['filename'] = qqfile

        except Fault, e:
            error = {'message': e.faultCode, 'data': {'debug': ''}}
            args = {'error': error, 'filename': qqfile}
        except Exception, e:
            error = {'message': e.message, 'data': {'debug': ''}}
            args = {'error': error, 'filename': qqfile}
        return req.make_response(simplejson.dumps(args))


class BinaryExtend(Binary):
    @openerpweb.httprequest
    def saveas(self, req, model, field, id=None, filename_field=None, **kw):
        if model == 'ir.attachment':
            attachment_obj = req.session.model(model)
            if attachment_obj.check_downloadable([int(id)], req.context):
                return super(BinaryExtend, self).saveas(req, model, field, id, filename_field, **kw)
            else:
                out = """<script language="javascript" type="text/javascript">
                    var win = window.top.window;
                    win.jQuery(win).trigger(%s, %s);
                </script>"""
                args = {'error': {'message': _('You have no privilege to download some of the attachments'), 'data': {'debug': ''}}}
                return req.make_response(simplejson.dumps(args))
        else:
            return super(BinaryExtend, self).saveas(req, model, field, id, filename_field, **kw)

    @openerpweb.httprequest
    def saveas_ajax(self, req, data, token):
        jdata = simplejson.loads(data)
        model = jdata['model']
        id = jdata.get('id', None)
        if model == 'ir.attachment':
            attachment_obj = req.session.model(model)
            if attachment_obj.check_downloadable([int(id)], req.context):
                return super(BinaryExtend, self).saveas_ajax(req, data, token)
            else:
                args =  {'message': _('You have no privilege to download some of the attachments'), 'data': {'debug': ''}}
                return req.make_response(simplejson.dumps(args))
        else:
            return super(BinaryExtend, self).saveas_ajax(req, data, token)
