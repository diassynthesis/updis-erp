import base64
import simplejson
from web_clupload.controllers.main import InternalHome
import openerp

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

        except Exception, e:
            args = {'error': e.faultCode, 'filename': qqfile}
        return req.make_response(simplejson.dumps(args))
