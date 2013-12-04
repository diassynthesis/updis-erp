# -*- coding: utf-8 -*-
import logging
import time
import urllib2
from up_tools.bigantlib import BigAntClient
from urllib import urlencode

from osv import osv, fields


class sms(osv.Model):
    _sms_gateway = "http://web.mobset.com/SDK/Sms_Send.asp"
    _name = "sms.sms"
    _order = "id desc"
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
        'type': fields.selection([('sms', 'SMS'), ('big_ant', 'Big Ant')], string="Message Type"),
    }
    _defaults = {
        'state': 'draft',
        'type': 'sms',
    }


    def process_send_message_in_queue(self, cr, uid, context=None):
        self.process_sms_queue(cr, 1, context=context)
        self.process_big_ant_queue(cr, 1, context=context)
        logging.getLogger('sms.sms').warning("SENDING SMS Message!")


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
                bigAntClient = BigAntClient()
                resp = bigAntClient.Employee___asmx.SendMessenge.post(**params)

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

    def send_sms_to_group(self, cr, uid, from_rec, content, model, res_id, group_id, context=None):

        model_pool = self.pool.get('ir.model.data')
        model_ids = model_pool.search(cr, 1, [('model', '=', 'res.groups'), ('name', '=', group_id)],
                                      context=context)

        models = model_pool.browse(cr, 1, model_ids, context=context)
        if models:
            groups_pool = self.pool.get("res.groups")
            group = groups_pool.browse(cr, 1, models[0].res_id, context=context)
            to = ','.join(
                [rid.mobile_phone.strip() for rid in group.users if rid.mobile_phone and rid.mobile_phone.strip()])

            if to:
                sms = self.pool.get('sms.sms')
                sid = sms.create(cr, uid, {'from': from_rec, 'to': to, 'content': content,
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
            [user.big_ant_login_name for user in users if user.big_ant_login_name])
        if to:
            sid = self.create(cr, uid,
                              {'to': to, 'subject': subject, 'content': content, 'model': model, 'res_id': res_id,
                               'type': 'big_ant'},
                              context=context)

    def send_big_ant_to_group(self, cr, uid, from_rec, subject, content, model, res_id, group_id, context=None):

        model_pool = self.pool.get('ir.model.data')
        model_ids = model_pool.search(cr, 1, [('model', '=', 'res.groups'), ('name', '=', group_id)],
                                      context=context)

        models = model_pool.browse(cr, 1, model_ids, context=context)
        if models:
            groups_pool = self.pool.get("res.groups")
            group = groups_pool.browse(cr, 1, models[0].res_id, context=context)
            to = ';'.join([user.big_ant_login_name for user in group.users if user.big_ant_login_name])

            if to:
                sms = self.pool.get('sms.sms')
                sid = sms.create(cr, uid, {'from': from_rec, 'to': to, 'subject': subject, 'content': content,
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
            to = ';'.join([user.big_ant_login_name for user in group.users if user.big_ant_login_name])

            if to:
                sms = self.pool.get('sms.sms')
                sid = sms.create(cr, uid, {'from': from_rec, 'to': to, 'subject': subject, 'content': content,
                                           'model': model, 'res_id': res_id, 'type': 'big_ant'},
                                 context=context)