from openerp.osv.orm import browse_record, _logger

__author__ = 'cysnake4713'

from openerp import SUPERUSER_ID
from openerp.osv import osv


class MailServerInherit(osv.osv):
    _inherit = 'ir.mail_server'

    def send_email(self, cr, uid, message, mail_server_id=None, smtp_server=None, smtp_port=None,
                   smtp_user=None, smtp_password=None, smtp_encryption=None, smtp_debug=False,
                   context=None):
        pass


class MailThreadInherit(osv.osv_abstract):
    _inherit = 'mail.thread'

    def message_track(self, cr, uid, ids, tracked_fields, initial_values, context=None):

        def convert_for_display(value, col_info):
            if not value and col_info['type'] == 'boolean':
                return 'False'
            if not value:
                return ''
            if col_info['type'] == 'many2one':
                return value[1]
            if col_info['type'] == 'selection':
                return dict(col_info['selection'])[value]
            if col_info['type'] == 'many2many':
                obj = self.pool.get(col_info['relation'])
                targets = obj.read(cr, SUPERUSER_ID, list(value), [obj._rec_name])
                rec_names = [t[obj._rec_name] for t in targets]
                return ','.join(rec_names)
            return value

        def format_message(message_description, tracked_values):
            message = ''
            if message_description:
                message = '<span>%s</span>' % message_description
            for name, change in tracked_values.items():
                message += '<div> &nbsp; &nbsp; &bull; <b>%s</b>: ' % change.get('col_info')
                if change.get('old_value'):
                    message += '%s &rarr; ' % change.get('old_value')
                message += '%s</div>' % change.get('new_value')
            return message

        if not tracked_fields:
            return True

        for record in self.read(cr, uid, ids, tracked_fields.keys(), context=context):
            initial = initial_values[record['id']]
            changes = []
            tracked_values = {}

            # generate tracked_values data structure: {'col_name': {col_info, new_value, old_value}}
            for col_name, col_info in tracked_fields.items():
                if record[col_name] == initial[col_name] and getattr(self._all_columns[col_name].column, 'track_visibility', None) == 'always':
                    tracked_values[col_name] = dict(col_info=col_info['string'],
                                                    new_value=convert_for_display(record[col_name], col_info))
                elif record[col_name] != initial[col_name]:
                    if getattr(self._all_columns[col_name].column, 'track_visibility', None) in ['always', 'onchange']:
                        tracked_values[col_name] = dict(col_info=col_info['string'],
                                                        old_value=convert_for_display(initial[col_name], col_info),
                                                        new_value=convert_for_display(record[col_name], col_info))
                    if col_name in tracked_fields:
                        changes.append(col_name)
            if not changes:
                continue

            # find subtypes and post messages or log if no subtype found
            subtypes = []
            for field, track_info in self._track.items():
                if field not in changes:
                    continue
                for subtype, method in track_info.items():
                    if method(self, cr, uid, record, context):
                        subtypes.append(subtype)

            posted = False
            for subtype in subtypes:
                try:
                    subtype_rec = self.pool.get('ir.model.data').get_object(cr, uid, subtype.split('.')[0], subtype.split('.')[1], context=context)
                except ValueError, e:
                    _logger.debug('subtype %s not found, giving error "%s"' % (subtype, e))
                    continue
                message = format_message(subtype_rec.description if subtype_rec.description else subtype_rec.name, tracked_values)
                self.message_post(cr, uid, record['id'], body=message, subtype=subtype, context=context)
                posted = True
            if not posted:
                message = format_message('', tracked_values)
                self.message_post(cr, uid, record['id'], body=message, context=context)
        return True

    def message_post(self, cr, uid, thread_id, body='', subject=None, type='notification',
                     subtype=None, parent_id=False, attachments=None, context=None,
                     content_subtype='html', **kwargs):
        msg_id = super(MailThreadInherit, self).message_post(cr, uid, thread_id, body, subject, type,
                                                             subtype, parent_id, attachments, context,
                                                             content_subtype, **kwargs)
        if type == 'comment':
            thread_id = thread_id[0] if isinstance(thread_id, list) else thread_id
            thread = self.browse(cr, uid, thread_id, context)
            # get href address
            http_address = self.pool['ir.config_parameter'].get_param(cr, uid, 'web.base.static.url', default='', context=context)
            http_address += "/#id=%s&amp;model=%s&amp;view_type=form" % (thread.id, thread._table_name)
            head = "<div><a href='%s'>%s</a></div><br/>" % (http_address, getattr(thread, thread._model._rec_name))
            # get user ids and sent bigant message
            partner_ids = [p.id for p in thread.message_follower_ids]
            user_ids = self.pool['res.users'].search(cr, SUPERUSER_ID, [('partner_id', 'in', partner_ids)], context=context)
            self.pool['sms.sms'].send_big_ant_to_users(cr, uid, from_rec=thread[thread._model._rec_name], subject=subject,
                                                       content=head + '<div>%s</div>' % body,
                                                       model=thread._table_name, res_id=thread.id, user_ids=user_ids, context=context)
        return msg_id