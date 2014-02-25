__author__ = 'cysnake4713'

from openerp.osv import osv, fields
from openerp.osv.orm import except_orm
from openerp.tools import eval

EXCLUDED_FIELDS = {'report_sxw_content', 'report_rml_content', 'report_sxw', 'report_rml', 'report_sxw_content_data', 'report_rml_content_data',
                   'search_view'}

#: Possible slots to bind an action to with :meth:`~.set_action`
ACTION_SLOTS = [
    "client_action_multi",  # sidebar wizard action
    "client_print_multi",  # sidebar report printing button
    "client_action_relate",  # sidebar related link
    "tree_but_open",  # double-click on item in tree view
    "tree_but_action",  # deprecated: same as tree_but_open
]


class IrAttachmentInherit(osv.osv):
    _inherit = 'ir.attachment'
    _columns = {
        'index_id': fields.integer('Index Id'),
        'index_model': fields.char('Index Model', 256),
    }


class IrValuesInherit(osv.osv):
    _inherit = 'ir.values'

    def get_actions(self, cr, uid, action_slot, model, res_id=False, context=None):
        """Retrieves the list of actions bound to the given model's action slot.
           See the class description for more details about the various action
           slots: :class:`~.ir_values`.

           :param string action_slot: the action slot to which the actions should be
                                      bound to - one of ``client_action_multi``,
                                      ``client_print_multi``, ``client_action_relate``,
                                      ``tree_but_open``.
           :param string model: model name
           :param int res_id: optional record id - will bind the action only to a
                              specific record of the model, not all records.
           :return: list of action tuples of the form ``(id, name, action_def)``,
                    where ``id`` is the ID of the default entry, ``name`` is the
                    action label, and ``action_def`` is a dict containing the
                    action definition as obtained by calling
                    :meth:`~openerp.osv.osv.osv.read` on the action record.
        """
        assert action_slot in ACTION_SLOTS, 'Illegal action slot value: %s' % action_slot
        # use a direct SQL query for performance reasons,
        # this is called very often
        query = """SELECT v.id, v.name, v.value FROM ir_values v
                   WHERE v.key = %s AND v.key2 = %s
                        AND v.model = %s
                        AND (v.res_id = %s
                             OR v.res_id IS NULL
                             OR v.res_id = 0)
                   ORDER BY v.id"""
        cr.execute(query, ('action', action_slot, model, res_id or None))
        results = {}
        for action in cr.dictfetchall():
            if not action['value']:
                continue  # skip if undefined
            action_model, id = action['value'].split(',')
            fields = [
                field
                for field in self.pool.get(action_model)._all_columns
                if field not in EXCLUDED_FIELDS]
            # FIXME: needs cleanup
            try:
                action_def = self.pool.get(action_model).read(cr, uid, int(id), fields, context)
                context_ref = action_def['context'] if 'context' in action_def else None
                #TODO: replace the find to re
                #TODO: domain seems no need
                domain_ref = action_def['domain'] if 'domain' in action_def else None
                # if domain_ref and context and 'eval_domain' in context and context['eval_domain'] is True:
                #     domain_ref = eval(domain_ref, context, {'context': context})
                #     action_def['domain'] = str(domain_ref)
                if context_ref and context and 'eval_context' in context and context['eval_context'] is True:
                    context_local = eval(context_ref, context, {'context': context})
                    context.update(context_local)
                    action_def['context'] = str(context)
                if action_def:
                    if action_model in ('ir.actions.report.xml', 'ir.actions.act_window',
                                        'ir.actions.wizard'):
                        groups = action_def.get('groups_id')
                        if groups:
                            cr.execute('SELECT 1 FROM res_groups_users_rel WHERE gid IN %s AND uid=%s',
                                       (tuple(groups), uid))
                            if not cr.fetchone():
                                if action['name'] == 'Menuitem':
                                    raise osv.except_osv('Error!',
                                                         'You do not have the permission to perform this operation!!!')
                                continue
                # keep only the first action registered for each action name
                results[action['name']] = (action['id'], action['name'], action_def)
            except except_orm:
                continue
        return sorted(results.values())