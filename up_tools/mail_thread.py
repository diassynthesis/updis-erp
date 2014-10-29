from openerp.osv.orm import browse_record, _logger, browse_null

__author__ = 'cysnake4713'

from openerp import SUPERUSER_ID
from openerp.osv import osv


def monkey_message_auto_subscribe(self, cr, uid, ids, updated_fields, context=None, values=None):
    """ Handle auto subscription. Two methods for auto subscription exist:

     - tracked res.users relational fields, such as user_id fields. Those fields
       must be relation fields toward a res.users record, and must have the
       track_visilibity attribute set.
     - using subtypes parent relationship: check if the current model being
       modified has an header record (such as a project for tasks) whose followers
       can be added as followers of the current records. Example of structure
       with project and task:

      - st_project_1.parent_id = st_task_1
      - st_project_1.res_model = 'project.project'
      - st_project_1.relation_field = 'project_id'
      - st_task_1.model = 'project.task'

    :param list updated_fields: list of updated fields to track
    :param dict values: updated values; if None, the first record will be browsed
                        to get the values. Added after releasing 7.0, therefore
                        not merged with updated_fields argumment.
    """
    subtype_obj = self.pool.get('mail.message.subtype')
    follower_obj = self.pool.get('mail.followers')
    new_followers = dict()

    # fetch auto_follow_fields: res.users relation fields whose changes are tracked for subscription
    user_field_lst = self._message_get_auto_subscribe_fields(cr, uid, updated_fields, context=context)

    # fetch header subtypes
    header_subtype_ids = subtype_obj.search(cr, uid, ['|', ('res_model', '=', False), ('parent_id.res_model', '=', self._name)], context=context)
    subtypes = subtype_obj.browse(cr, uid, header_subtype_ids, context=context)

    # if no change in tracked field or no change in tracked relational field: quit
    relation_fields = set([subtype.relation_field for subtype in subtypes if subtype.relation_field is not False])
    if not any(relation in updated_fields for relation in relation_fields) and not user_field_lst:
        return True

    # legacy behavior: if values is not given, compute the values by browsing
    # @TDENOTE: remove me in 8.0
    if values is None:
        record = self.browse(cr, uid, ids[0], context=context)
        for updated_field in updated_fields:
            field_value = getattr(record, updated_field)
            if isinstance(field_value, browse_record):
                field_value = field_value.id
            elif isinstance(field_value, browse_null):
                field_value = False
            values[updated_field] = field_value

    # find followers of headers, update structure for new followers
    headers = set()
    for subtype in subtypes:
        if subtype.relation_field and values.get(subtype.relation_field):
            headers.add((subtype.res_model, values.get(subtype.relation_field)))
    if headers:
        header_domain = ['|'] * (len(headers) - 1)
        for header in headers:
            header_domain += ['&', ('res_model', '=', header[0]), ('res_id', '=', header[1])]
        header_follower_ids = follower_obj.search(
            cr, SUPERUSER_ID,
            header_domain,
            context=context
        )
        for header_follower in follower_obj.browse(cr, SUPERUSER_ID, header_follower_ids, context=context):
            for subtype in header_follower.subtype_ids:
                if subtype.parent_id and subtype.parent_id.res_model == self._name:
                    new_followers.setdefault(header_follower.partner_id.id, set()).add(subtype.parent_id.id)
                elif subtype.res_model is False:
                    new_followers.setdefault(header_follower.partner_id.id, set()).add(subtype.id)

    # add followers coming from res.users relational fields that are tracked
    user_ids = [values[name] for name in user_field_lst if values.get(name)]
    if user_ids and isinstance(user_ids[0], list):
        user_ids = user_ids[0][0][2]
    user_pids = [user.partner_id.id for user in self.pool.get('res.users').browse(cr, SUPERUSER_ID, user_ids, context=context)]
    for partner_id in user_pids:
        new_followers.setdefault(partner_id, None)

    for pid, subtypes in new_followers.items():
        subtypes = list(subtypes) if subtypes is not None else None
        self.message_subscribe(cr, uid, ids, [pid], subtypes, context=context)

    # find first email message, set it as unread for auto_subscribe fields for them to have a notification
    if user_pids:
        for record_id in ids:
            message_obj = self.pool.get('mail.message')
            msg_ids = message_obj.search(cr, SUPERUSER_ID, [
                ('model', '=', self._name),
                ('res_id', '=', record_id),
                ('type', '=', 'email')], limit=1, context=context)
            if not msg_ids:
                msg_ids = message_obj.search(cr, SUPERUSER_ID, [
                    ('model', '=', self._name),
                    ('res_id', '=', record_id)], limit=1, context=context)
            if msg_ids:
                self.pool.get('mail.notification')._notify(cr, uid, msg_ids[0], partners_to_notify=user_pids, context=context)


from openerp.addons.mail.mail_thread import mail_thread

mail_thread.message_auto_subscribe = monkey_message_auto_subscribe


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
        user_ids = []
        # if have group to process
        group_xml_ids = kwargs.pop('group_xml_ids', '')
        if group_xml_ids:
            user_ids = []
            for group_xml_id in group_xml_ids.split(','):
                (module, xml_id) = group_xml_id.split('.')
                group = self.pool.get('ir.model.data').get_object(cr, 1, module, xml_id, context=context)
                if group:
                    user_ids += [user.id for user in group.users]
        # if have user_ids to process
        user_ids += kwargs.pop('user_ids', [])
        # if have config group
        config_group_id = kwargs.pop('config_group_id', '')
        if config_group_id:
            model_pool = self.pool.get('ir.model.data')
            model_ids = model_pool.search(cr, 1, [('model', '=', 'project.config.sms'), ('name', '=', config_group_id)],
                                          context=context)
            models = model_pool.browse(cr, 1, model_ids, context=context)
            if models:
                groups_pool = self.pool.get("project.config.sms")
                group = groups_pool.browse(cr, 1, models[0].res_id, context=context)
                user_ids += [user.id for user in group.users]
        partner_ids = [user.partner_id.id for user in self.pool.get('res.users').browse(cr, uid, user_ids, context=context)]

        msg_id = super(MailThreadInherit, self).message_post(cr, uid, thread_id, body, subject, type,
                                                             subtype, parent_id, attachments, context,
                                                             content_subtype, partner_ids=partner_ids)
        is_send_ant = kwargs.pop('is_send_ant', True)
        # Send big ant message
        if type == 'comment' and is_send_ant:
            thread_id = thread_id[0] if isinstance(thread_id, list) else thread_id
            thread = self.browse(cr, uid, thread_id, context)
            # get href address
            http_address = self.pool['ir.config_parameter'].get_param(cr, uid, 'web.base.static.url', default='', context=context)
            http_address += "/#id=%s&model=%s&view_type=form" % (thread.id, thread._table_name)
            name = getattr(thread, thread._model._rec_name) if hasattr(thread, thread._model._rec_name) else '%s,%s' % (
                thread._model._name, str(thread.id))
            head = "<div><a href='%s' target='_blank'>%s</a></div><br/>" % (http_address, name)
            # get user ids and sent bigant message
            big_partner_ids = [p.id for p in thread.message_follower_ids] + partner_ids
            user_ids = self.pool['res.users'].search(cr, SUPERUSER_ID, [('partner_id', 'in', big_partner_ids)], context=context)
            self.pool['sms.sms'].send_big_ant_to_users(cr, uid, from_rec=name, subject=subject,
                                                       content=head + '<div>%s</div>' % body,
                                                       model=thread._table_name, res_id=thread.id, user_ids=user_ids, context=context)
        is_send_sms = kwargs.pop('is_send_sms', False)
        sms_body = kwargs.pop('sms_body', '')
        if is_send_sms:
            user_ids = self.pool['res.users'].search(cr, SUPERUSER_ID, [('partner_id', 'in', partner_ids)], context=context)
            sms_body = sms_body if sms_body else body
            self.pool['sms.sms'].send_sms_to_users(cr, uid, from_rec=name,
                                                   content=sms_body,
                                                   model=thread._table_name, res_id=thread.id, user_ids=user_ids, context=context)
        return msg_id

    def message_subscribe_groups(self, cr, uid, ids, group_xml_ids=None, subtype_ids=None, context=None):
        """ Wrapper on message_subscribe, using users. If user_ids is not
            provided, subscribe uid instead. """
        if group_xml_ids:
            user_ids = []
            for group_xml_id in group_xml_ids.split(','):
                (module, xml_id) = group_xml_id.split('.')
                group = self.pool.get('ir.model.data').get_object(cr, 1, module, xml_id, context=context)
                if group:
                    user_ids += [user.id for user in group.users]
            return self.message_subscribe_users(cr, uid, ids, user_ids=user_ids, subtype_ids=subtype_ids, context=context)
        return True

    def message_subscribe_config_groups(self, cr, uid, ids, config_group_id=None, subtype_ids=None, context=None):
        if config_group_id:
            model_pool = self.pool.get('ir.model.data')
            model_ids = model_pool.search(cr, 1, [('model', '=', 'project.config.sms'), ('name', '=', config_group_id)],
                                          context=context)
            models = model_pool.browse(cr, 1, model_ids, context=context)
            if models:
                groups_pool = self.pool.get("project.config.sms")
                group = groups_pool.browse(cr, 1, models[0].res_id, context=context)
                user_ids = [user.id for user in group.users]
                return self.message_subscribe_users(cr, uid, ids, user_ids=user_ids, subtype_ids=subtype_ids, context=context)
        return True