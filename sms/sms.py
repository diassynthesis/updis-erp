import logging
import time
from urllib2 import urlopen
from urllib import urlencode

from osv import osv, fields


class sms(osv.Model):
    _sms_gateway = "http://web.mobset.com/SDK/Sms_Send.asp?"
    _name = "sms.sms"
    _columns = {
        'content': fields.text("Content", size=128),
        'from': fields.char("From", size=200),
        'to': fields.char('To', size=2000),
        'sent_date': fields.datetime("Send date"),
        'model': fields.char("Related Document Model", size=128, select=1),
        'res_id': fields.integer('Related Document ID', select=1),
        'sms_server_id': fields.char("SMS ID From Gateway", size=2000),
        'state': fields.selection([('draft', 'Draft'), ('error', 'Error'), ('sent', 'Sent')], 'State', required=True,
                                  size=64),
    }
    _defaults = {
        'state': 'draft',
    }

    def process_sms_queue(self, cr, uid, context=None):
        params = {
            'CorpID': '118775',
            'LoginName': '72620872',
            'Passwd': '047243',
        }
        sms_ids = self.search(cr, uid, [('state', '=', 'draft')], context=context)
        for sms in self.browse(cr, uid, sms_ids, context):
            params['send_no'] = sms.to
            params['msg'] = sms.content.encode('gbk')
            resp = urlopen(self._sms_gateway + urlencode(params))
            # import pdb;pdb.set_trace()
            if resp.code == 200:
                sms_server_id = resp.read()
                self.write(cr, uid, [sms.id], {
                    'sms_server_id': sms_server_id,
                    'state': 'sent',
                    'sent_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                })
            else:
                logging.getLogger('sms.sms').warning("SENDING SMS!")
                self.write(cr, uid, [sms.id], {
                    'state': 'error',
                    'sent_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                })
        logging.getLogger('sms.sms').warning("SENDING SMS!")
