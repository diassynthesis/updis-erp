from openerp.osv.orm import browse_record, _logger

__author__ = 'cysnake4713'

from openerp import SUPERUSER_ID
from openerp.osv import osv


class MailThreadInherit(osv.osv_abstract):
    _inherit = 'mail.thread'

    def message_auto_subscribe(self, cr, uid, ids, updated_fields, context=None):
        """
            1. fetch project subtype related to task (parent_id.res_model = 'project.task')
            2. for each project subtype: subscribe the follower to the task
        """
        subtype_obj = self.pool.get('mail.message.subtype')
        follower_obj = self.pool.get('mail.followers')

        # fetch auto_follow_fields
        user_field_lst = self._message_get_auto_subscribe_fields(cr, uid, updated_fields, context=context)

        # fetch related record subtypes
        related_subtype_ids = subtype_obj.search(cr, uid, ['|', ('res_model', '=', False), ('parent_id.res_model', '=', self._name)], context=context)
        subtypes = subtype_obj.browse(cr, uid, related_subtype_ids, context=context)
        default_subtypes = [subtype for subtype in subtypes if subtype.res_model == False]
        related_subtypes = [subtype for subtype in subtypes if subtype.res_model != False]
        relation_fields = set([subtype.relation_field for subtype in subtypes if subtype.relation_field != False])
        if (not related_subtypes or not any(relation in updated_fields for relation in relation_fields)) and not user_field_lst:
            return True

        for record in self.browse(cr, uid, ids, context=context):
            new_followers = dict()
            parent_res_id = False
            parent_model = False
            for subtype in related_subtypes:
                if not subtype.relation_field or not subtype.parent_id:
                    continue
                if not subtype.relation_field in self._columns or not getattr(record, subtype.relation_field, False):
                    continue
                parent_res_id = getattr(record, subtype.relation_field).id
                parent_model = subtype.res_model
                follower_ids = follower_obj.search(cr, SUPERUSER_ID, [
                    ('res_model', '=', parent_model),
                    ('res_id', '=', parent_res_id),
                    ('subtype_ids', 'in', [subtype.id])
                ], context=context)
                for follower in follower_obj.browse(cr, SUPERUSER_ID, follower_ids, context=context):
                    new_followers.setdefault(follower.partner_id.id, set()).add(subtype.parent_id.id)

            if parent_res_id and parent_model:
                for subtype in default_subtypes:
                    follower_ids = follower_obj.search(cr, SUPERUSER_ID, [
                        ('res_model', '=', parent_model),
                        ('res_id', '=', parent_res_id),
                        ('subtype_ids', 'in', [subtype.id])
                    ], context=context)
                    for follower in follower_obj.browse(cr, SUPERUSER_ID, follower_ids, context=context):
                        new_followers.setdefault(follower.partner_id.id, set()).add(subtype.id)

            # add followers coming from res.users relational fields that are tracked
            user_ids = []
            for name in user_field_lst:
                if getattr(record, name):
                    if isinstance(getattr(record, name), list):
                        user_ids += [user.id for user in getattr(record, name)]
                    else:
                        user_ids += [getattr(record, name).id]
            user_id_partner_ids = [user.partner_id.id for user in self.pool.get('res.users').browse(cr, SUPERUSER_ID, user_ids, context=context)]
            for partner_id in user_id_partner_ids:
                new_followers.setdefault(partner_id, None)

            for pid, subtypes in new_followers.items():
                subtypes = list(subtypes) if subtypes is not None else None
                self.message_subscribe(cr, uid, [record.id], [pid], subtypes, context=context)

            # find first email message, set it as unread for auto_subscribe fields for them to have a notification
            if user_id_partner_ids:
                msg_ids = self.pool.get('mail.message').search(cr, uid, [
                    ('model', '=', self._name),
                    ('res_id', '=', record.id),
                    ('type', '=', 'email')], limit=1, context=context)
                if not msg_ids and record.message_ids:
                    msg_ids = [record.message_ids[-1].id]
                if msg_ids:
                    self.pool.get('mail.notification')._notify(cr, uid, msg_ids[0], partners_to_notify=user_id_partner_ids, context=context)

        return True

    def message_track(self, cr, uid, ids, tracked_fields, initial_values, context=None):

        def convert_for_display(self, value, col_info):
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
                                                    new_value=convert_for_display(self, record[col_name], col_info))
                elif record[col_name] != initial[col_name]:
                    if getattr(self._all_columns[col_name].column, 'track_visibility', None) in ['always', 'onchange']:
                        tracked_values[col_name] = dict(col_info=col_info['string'],
                                                        old_value=convert_for_display(self, initial[col_name], col_info),
                                                        new_value=convert_for_display(self, record[col_name], col_info))
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