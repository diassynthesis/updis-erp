# -*- coding: utf-8 -*-
import logging
import time
import urllib2
from up_tools.bigantlib import BigAntClient
from urllib import urlencode

from openerp.osv import osv, fields
from up_tools.rtxlib import RtxClient


class sms(osv.Model):
    _sms_gateway = "http://web.mobset.com/SDK/Sms_Send.asp"
    _name = "sms.sms"
    _order = "id desc"
    _bigAntClient = BigAntClient()

    _rtx_client = RtxClient()

    _columns = {
        'subject': fields.char('Subject', size=256),
        'content': fields.text("Content", size=2000),
        'from': fields.char("From", size=200),
        'to': fields.char('To', size=2000),
        'sent_date': fields.datetime("Send date"),
        'model': fields.char("Related Document Model", size=128, select=1),
        'res_id': fields.integer('Related Document ID', select=1),
        'sms_server_id': fields.char("SMS ID From Gateway", size=2000),
        'state': fields.selection([('draft', 'Draft'), ('error', 'Error'), ('sent', 'Sent')], 'State', required=True,
                                  size=64),
        'type': fields.selection([('sms', 'SMS'), ('big_ant', 'RTX')], string="Message Type"),
    }
    _defaults = {
        'state': 'draft',
        'type': 'sms',
    }

    def process_send_message_in_queue(self, cr, uid, context=None):
        self.process_sms_queue(cr, 1, context=context)
        self.process_rtx_message(cr, 1, context)
        logging.getLogger('sms.sms').warning("SENDING SMS Message!")

    def process_rtx_message(self, cr, uid, context=None):
        sms_ids = self.search(cr, uid, [('state', '=', 'draft'), ('type', '=', 'big_ant')], context=context)
        # params = {'sender': self._rtx_user, 'SenderPwd': self._rtx_password, 'SessionId': self._session_id, 'key': self._rtx_key}
        params = {'key': self._rtx_client.rtx_key, 'time': 60000}
        for sms in self.browse(cr, uid, sms_ids, context):
            try:
                params['Receivers'] = sms.to
                params['title'] = sms.subject
                params['msg'] = sms.content
                result = self._rtx_client.get_client().SendNotify(**params)
                self.write(cr, uid, [sms.id], {
                    'state': 'sent',
                    'sent_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'sms_server_id': str(result),
                })

            except Exception, e:
                logging.getLogger('sms.sms').error("sending RTX failed!")
                self.write(cr, uid, [sms.id], {
                    'state': 'error',
                    'sent_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'sms_server_id': e,
                })

    def process_big_ant_queue(self, cr, uid, context=None):
        params = {
            'bigantServer': '10.100.100.200',
            'port': '6660',
            'sendLoginName': 'xinxi',
            'passwordType': 0,
            'sendPassword': 'xinxi',
            'contentType': 'Text/Html',
            'sendUserName': '',
            'msgId': '',

        }
        sms_ids = self.search(cr, uid, [('state', '=', 'draft'), ('type', '=', 'big_ant')], context=context)
        for sms in self.browse(cr, uid, sms_ids, context):
            try:
                params['recvLoginNames'] = sms.to
                params['subject'] = sms.subject
                params['content'] = sms.content
                resp = self._bigAntClient.Employee___asmx.SendMessenge.post(**params)

                if resp.text == "1":
                    sms_server_id = 'Success'
                    self.write(cr, uid, [sms.id], {
                        'sms_server_id': sms_server_id,
                        'state': 'sent',
                        'sent_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    })
                elif resp.text == "0":
                    logging.getLogger('sms.sms').warning("SENDING Big Ant Message failed!")
                    self.write(cr, uid, [sms.id], {
                        'state': 'error',
                        'sent_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'sms_server_id': u"网络链接失败",
                    })
                elif resp.text == "205":
                    logging.getLogger('sms.sms').warning("SENDING Big Ant Message failed!")
                    self.write(cr, uid, [sms.id], {
                        'state': 'error',
                        'sent_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'sms_server_id': u"帐号或密码错误",
                    })
                else:
                    logging.getLogger('sms.sms').warning("SENDING Big Ant Message failed!")
                    self.write(cr, uid, [sms.id], {
                        'state': 'error',
                        'sent_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'sms_server_id': u"未知原因出错%s" % resp.text,
                    })

            except UnicodeEncodeError, e:
                logging.getLogger('sms.sms').error("sending Big Ant Message failed!")
                self.write(cr, uid, [sms.id], {
                    'state': 'error',
                    'sent_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'sms_server_id': e.reason,
                })
            except Exception, e:
                logging.getLogger('sms.sms').error("sending Big Ant Message failed!")
                self.write(cr, uid, [sms.id], {
                    'state': 'error',
                    'sent_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'sms_server_id': str(e),
                })


    def process_sms_queue(self, cr, uid, context=None):
        params = {
            'CorpID': '118775',
            'LoginName': '72620872',
            'Passwd': '047243',
        }
        sms_ids = self.search(cr, uid, [('state', '=', 'draft'), ('type', '=', 'sms')], context=context)
        for sms in self.browse(cr, uid, sms_ids, context):
            try:
                params['send_no'] = sms.to
                params['msg'] = sms.content.encode('gbk')
                resp = urllib2.urlopen(self._sms_gateway, urlencode(params), timeout=45)

                if resp.code == 200:
                    sms_server_id = resp.read().decode('gbk')
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
                        'sms_server_id': 'response error ==>' + resp.code,
                    })
            except UnicodeEncodeError, e:
                logging.getLogger('sms.sms').error("sending message error!")
                self.write(cr, uid, [sms.id], {
                    'state': 'error',
                    'sent_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'sms_server_id': e.reason,
                })
            except Exception, e:
                logging.getLogger('sms.sms').error("sending message error!")
                self.write(cr, uid, [sms.id], {
                    'state': 'error',
                    'sent_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'sms_server_id': str(e),
                })

    def send_sms_to_group(self, cr, uid, from_rec, content, model, res_id, group_xml_id, context=None):
        (module, xml_id) = group_xml_id.split('.')
        group = self.pool.get('ir.model.data').get_object(cr, 1, module, xml_id, context=context)
        if group:
            to = ','.join(
                [rid.mobile_phone.strip() for rid in group.users if rid.mobile_phone and rid.mobile_phone.strip()])

            if to:
                self.create(cr, uid, {'from': from_rec, 'to': to, 'content': content,
                                      'model': model, 'res_id': res_id},
                            context=context)

    def send_sms_to_users(self, cr, uid, users, from_rec, content, model, res_id, context=None):
        to = ','.join(
            [rid.mobile_phone.strip() for rid in users if rid.mobile_phone and rid.mobile_phone.strip()])
        if to:
            sid = self.create(cr, uid, {'to': to, 'content': content, 'model': model, 'res_id': res_id},
                              context=context)


    def send_sms_to_config_group(self, cr, uid, config_group_id, from_rec, content, model, res_id, context=None):
        model_pool = self.pool.get('ir.model.data')
        model_ids = model_pool.search(cr, 1, [('model', '=', 'project.config.sms'), ('name', '=', config_group_id)],
                                      context=context)
        models = model_pool.browse(cr, 1, model_ids, context=context)
        if models:
            groups_pool = self.pool.get("project.config.sms")
            group = groups_pool.browse(cr, 1, models[0].res_id, context=context)
            to = ','.join(
                [rid.mobile_phone.strip() for rid in group.users if rid.mobile_phone and rid.mobile_phone.strip()])

            if to:
                sms = self.pool.get('sms.sms')
                sid = sms.create(cr, uid, {'from': from_rec, 'to': to, 'content': content,
                                           'model': model, 'res_id': res_id},
                                 context=context)


    def send_big_ant_to_users(self, cr, uid, users, from_rec, subject, content, model, res_id, context=None):
        to = ';'.join(
            [user.login for user in users if user.login])
        if to:
            sid = self.create(cr, uid,
                              {'to': to, 'subject': subject, 'content': content, 'model': model, 'res_id': res_id,
                               'type': 'big_ant'},
                              context=context)

    def send_big_ant_to_group(self, cr, uid, from_rec, subject, content, model, res_id, group_xml_id, context=None):
        (module, xml_id) = group_xml_id.split('.')
        group = self.pool.get('ir.model.data').get_object(cr, 1, module, xml_id, context=context)
        if group:
            to = ';'.join([user.login for user in group.users if user.login])
            if to:
                self.create(cr, uid, {'from': from_rec, 'to': to, 'subject': subject, 'content': content,
                                      'model': model, 'res_id': res_id, 'type': 'big_ant'},
                            context=context)

    def send_big_ant_to_config_group(self, cr, uid, config_group_id, from_rec, subject, content, model, res_id,
                                     context=None):
        model_pool = self.pool.get('ir.model.data')
        model_ids = model_pool.search(cr, 1, [('model', '=', 'project.config.sms'), ('name', '=', config_group_id)],
                                      context=context)
        models = model_pool.browse(cr, 1, model_ids, context=context)
        if models:
            groups_pool = self.pool.get("project.config.sms")
            group = groups_pool.browse(cr, 1, models[0].res_id, context=context)
            to = ';'.join([user.login for user in group.users if user.login])

            if to:
                sms = self.pool.get('sms.sms')
                sid = sms.create(cr, uid, {'from': from_rec, 'to': to, 'subject': subject, 'content': content,
                                           'model': model, 'res_id': res_id, 'type': 'big_ant'},
                                 context=context)