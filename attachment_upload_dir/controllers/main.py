__author__ = 'cysnake4713'
# -*- coding: utf-8 -*-

from openerp.addons.web.controllers.main import *
from openerp.addons.web.controllers import main
import simplejson


@openerpweb.httprequest
def upload_attachment(self, req, callback, model, id, ufile, upload_context="{}", index_model="", index_id=0):
    Model = req.session.model('ir.attachment')
    out = """<script language="javascript" type="text/javascript">
                    var win = window.top.window;
                    win.jQuery(win).trigger(%s, %s);
                </script>"""
    context = eval(upload_context)
    try:
        attachment_id = Model.create(
            {
                'name': ufile.filename,
                'datas': base64.encodestring(ufile.read()),
                'datas_fname': ufile.filename,
                'res_model': model,
                'res_id': int(id),
                'index_id': int(index_id),
                'index_model': index_model,
            }, context)
        args = {
            'filename': ufile.filename,
            'id': attachment_id
        }
    except xmlrpclib.Fault, e:
        args = {'error': e.faultCode}
    return out % (simplejson.dumps(callback), simplejson.dumps(args))


main.Binary.upload_attachment = upload_attachment

