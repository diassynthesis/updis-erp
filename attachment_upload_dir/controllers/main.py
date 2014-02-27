__author__ = 'cysnake4713'
# -*- coding: utf-8 -*-

from openerp.addons.web.controllers.main import *
from openerp.addons.web.controllers import main
import simplejson


@openerpweb.httprequest
def upload_attachment(self, req, callback, model, id, ufile, res_id=None, res_model=None, res_context="{}"):
    Model = req.session.model('ir.attachment')
    out = """<script language="javascript" type="text/javascript">
                    var win = window.top.window;
                    win.jQuery(win).trigger(%s, %s);
                </script>"""
    context = eval(res_context)
    model = res_model or model
    id = res_id or id
    try:
        attachment_id = Model.create(
            {
                'name': ufile.filename,
                'datas': base64.encodestring(ufile.read()),
                'datas_fname': ufile.filename,
                'res_model': model,
                'res_id': int(id),
            }, context)
        args = {
            'filename': ufile.filename,
            'id': attachment_id
        }
    except xmlrpclib.Fault, e:
        args = {'error': e.faultCode}
    return out % (simplejson.dumps(callback), simplejson.dumps(args))


main.Binary.upload_attachment = upload_attachment

