# -*- encoding:utf-8 -*-
import datetime
from openerp.osv import fields
from openerp.osv import osv

__author__ = 'cysnake4713'


class updis_contract_expenses(osv.osv):
    _name = 'project.contract.expenses'
    _rec_name = 'price'
    _order = 'obtain_date'
    _columns = {
        'obtain_date': fields.date('Obtain Date', required=True),
        'price': fields.float(string='Obtain Price', digits=(16, 4)),
        'comment': fields.text(string="Comment"),
        'handler': fields.many2one('hr.employee', string='Handler'),
        'contract_id': fields.many2one('project.contract.contract', string="Contract"),
    }

    _defaults = {
        'obtain_date': lambda *a: str(datetime.date.today()),
    }


class updis_contract_invoice(osv.osv):
    _name = 'project.contract.invoice'
    _description = 'Project Contract Invoice'
    _rec_name = 'number'
    _order = 'obtain_date'
    _columns = {
        'number': fields.char('Invoice No.', size=64, ),
        'obtain_date': fields.date('Invoice Create Date', required=True),
        'price': fields.float(string='Price', digits=(16, 4)),
        'comment': fields.text(string="Comment"),
        'handler': fields.many2one('hr.employee', string='Handler'),
        'contract_id': fields.many2one('project.contract.contract', string="Contract"),
        'income_ids': fields.many2many('project.contract.income', 'contract_invoice_income_rels', 'invoice_id',
                                       'income_id', string='Incomes'),
        'is_clear': fields.boolean(string="is Invoice Clear"),
        'clear_date': fields.date(string='Invoice Clear Date'),
        "is_import": fields.boolean(string="Is Import"),
    }

    _defaults = {
        'obtain_date': lambda *a: str(datetime.date.today()),
        'is_import': False,
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(updis_contract_invoice, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        if not record_id:
            return res

        if 'contract_id' in fields:
            res['contract_id'] = record_id
        return res

    def all_contract_invoice_action(self, cr, uid, context=None):
        domain = []
        if self.user_has_groups(cr, uid, 'up_contract.group_up_contract_partial_user', context=context):
            hr_id = self.pool.get('hr.employee').search(cr, uid, [("user_id", '=', uid)], context=context)
            if hr_id:
                hr_record = self.pool.get('hr.employee').browse(cr, uid, hr_id[0], context=context)
                user_department_id = hr_record.department_id.id if hr_record.department_id else 0
                domain = [('contract_id.design_department.id', '=', user_department_id)]
            else:
                domain = [('contract_id.design_department.id', '=', 0)]
        if self.user_has_groups(cr, uid, 'up_contract.group_up_contract_user', context=context):
            domain = []

        view_form = self.pool.get('ir.model.data').search(cr, 1, [('model', '=', 'ir.ui.view'),
                                                                  ('name', '=',
                                                                   'project_contract_invoice_form_menu')],
                                                          context=context)
        if view_form:
            view_form_id = self.pool.get('ir.model.data').read(cr, 1, view_form[0], ['res_id'])

        view_tree = self.pool.get('ir.model.data').search(cr, 1, [('model', '=', 'ir.ui.view'),
                                                                  ('name', '=',
                                                                   'project_contract_invoice_tree_menu')],
                                                          context=context)
        if view_tree:
            view_tree_id = self.pool.get('ir.model.data').read(cr, 1, view_tree[0], ['res_id'])
        return {
            'name': u'已开发票查询',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'project.contract.invoice',
            'target': 'current',
            'domain': domain,
            'context': context,
            'views': [(view_tree_id['res_id'], 'tree'), (view_form_id['res_id'], 'form')],
        }


class updis_contract_income(osv.osv):
    _name = 'project.contract.income'
    _rec_name = 'price'
    _order = 'obtain_date'
    _columns = {
        'obtain_date': fields.date('Obtain Date', required=True),
        'price': fields.float(string='Obtain Price', digits=(16, 4)),
        'comment': fields.text(string="Comment"),
        'handler': fields.many2one('hr.employee', string='Handler'),
        'contract_id': fields.many2one('project.contract.contract', string="Contract"),
        'invoice_ids': fields.many2many('project.contract.invoice', 'contract_invoice_income_rels', 'income_id',
                                        'invoice_id', string='Invoices'),
        "is_import": fields.boolean(string="Is Import"),
    }

    _defaults = {
        'obtain_date': lambda *a: str(datetime.date.today()),
        'is_import': False,
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(updis_contract_income, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        if not record_id:
            return res

        if 'contract_id' in fields:
            res['contract_id'] = record_id
        return res

    def all_contract_income_action(self, cr, uid, context=None):
        domain = []
        if self.user_has_groups(cr, uid, 'up_contract.group_up_contract_partial_user', context=context):
            hr_id = self.pool.get('hr.employee').search(cr, uid, [("user_id", '=', uid)], context=context)
            if hr_id:
                hr_record = self.pool.get('hr.employee').browse(cr, uid, hr_id[0], context=context)
                user_department_id = hr_record.department_id.id if hr_record.department_id else 0
                domain = [('contract_id.design_department.id', '=', user_department_id)]
            else:
                domain = [('contract_id.design_department.id', '=', 0)]
        if self.user_has_groups(cr, uid, 'up_contract.group_up_contract_user', context=context):
            domain = []

        view_form = self.pool.get('ir.model.data').search(cr, 1, [('model', '=', 'ir.ui.view'),
                                                                  ('name', '=',
                                                                   'project_contract_income_form_menu')],
                                                          context=context)
        if view_form:
            view_form_id = self.pool.get('ir.model.data').read(cr, 1, view_form[0], ['res_id'])

        view_tree = self.pool.get('ir.model.data').search(cr, 1, [('model', '=', 'ir.ui.view'),
                                                                  ('name', '=',
                                                                   'project_contract_income_tree_menu')],
                                                          context=context)
        if view_tree:
            view_tree_id = self.pool.get('ir.model.data').read(cr, 1, view_tree[0], ['res_id'])
        return {
            'name': u'收费进度查询',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'project.contract.income',
            'target': 'current',
            'domain': domain,
            'context': context,
            'views': [(view_tree_id['res_id'], 'tree'), (view_form_id['res_id'], 'form')],
        }


class updis_contract_contract(osv.osv):
    _name = 'project.contract.contract'
    _order = 'id desc'
    _log_access = True
    _rec_name = "name"
    _columns = {

        'create_date': fields.datetime('Created on', select=True),
        'create_uid': fields.many2one('res.users', 'Author', select=True),
        'write_date': fields.datetime('Modification date', select=True),
        'write_uid': fields.many2one('res.users', 'Last Contributor', select=True),

        'name': fields.char(size=128, string="Contract Name", required=True),
        'type': fields.selection([('common', u'Common Contract'), ('third_party', u'Third Party')], required=True,
                                 string='Contract Type'),
        'sign_date': fields.date(string='Contract Sign Date'),
        'third_party_sign_date': fields.date(string='Contract Third Party Sign Date'),
        'customer': fields.many2many('res.partner', 'contract_partner_rel', 'contract_id', 'partner_id',
                                     string='Customers'),
        'customer_type': fields.selection([('JC200511210001', u"规划部门"),
                                           ('JC200511210002', u"其他政府部门"),
                                           ('JC200511210003', u"企业")], string="Customer Type"),
        'customer_contact': fields.many2many('res.partner', 'contract_contact_partner_rel', 'contract_contact_id',
                                             'partner_id', string="Customer Contacts"),
        'third_party_company': fields.many2many('res.partner', 'contract_third_party_company_rel', 'contract_id',
                                                'partner_id',
                                                string='Third Party Company'),
        'third_party_company_contact': fields.many2many('res.partner', 'contract_contact_third_party_company_rel',
                                                        'contract_contact_id',
                                                        'partner_id', string="Third Party Company Contacts"),
        'price': fields.float(string='Contract Price', digits=(16, 4)),
        'number': fields.char(string='Contract No.', size=128),
        'city_level_number': fields.char(string='City Contract No.', size=128),
        'city_comment': fields.char(size=128, string="City Comment"),
        'comment': fields.text(string="Comment"),
        "change": fields.selection([(u"转让", u"转让"), (u"正常", u"正常"), (u"变更", u"变更")], string="Contract Change"),

        'income_ids': fields.one2many('project.contract.income', 'contract_id', string='Incomes', ondelete="cascade"),
        'invoice_ids': fields.one2many('project.contract.invoice', 'contract_id', string='Invoices',
                                       ondelete="cascade"),
        'expenses_ids': fields.one2many('project.contract.expenses', 'contract_id', string='Third Party Expenses',
                                        ondelete="cascade"),
        'entrust_type': fields.selection(
            [('WT200508180001', u'深圳规划局'), ('WT200508180002', u"深圳市其他"), ('WT200508180003', u"市外"),
             ('WT200509020001', u"其他")], string="Entrust Type"),
        ##Tender
        "import_tender_type": fields.char(size=128, string="Import Tender Type"),
        "import_tender_result": fields.char(size=128, string="Import Tender Result"),
        "import_contin": fields.char(size=128, string="Import Tender Contin"),
        "tender_phone": fields.char(size=128, string="Tender Phone"),
        "import_number": fields.char(size=128, string="Import Number"),
        "is_import": fields.boolean(string="Is Import"),

        'project_id': fields.many2one('project.project', string="Project"),
        'project_number': fields.related('project_id', 'xiangmubianhao', type='char', string="Project Number"),
        'project_category': fields.related('project_id', 'categories_id', type="many2one",
                                           relation="project.upcategory", string="Project Category"),
        'design_department': fields.related('project_id', 'chenjiebumen_id', type="many2one",
                                            relation="hr.department", string='Design Department'),
        'project_scale': fields.related('project_id', 'guimo', type='char', string="Project Scale"),
        'project_level': fields.related('project_id', 'guanlijibie', type='selection',
                                        selection=[('LH200307240001', u'院级'), ('LH200307240002', u'所级')],
                                        string='Project Level'),
        'project_is_tender': fields.related('project_id', 'shifoutoubiao', type='boolean', string="Project Is Tender"),
        'project_tender_type': fields.related('project_id', 'toubiaoleibie', type='selection',
                                              selection=[('business', u'商务标'), ('technology', u'技术标'),
                                                         ('complex', u'综合标')],
                                              string='Project Tender Type'),
        'project_is_city': fields.related('project_id', 'shizhenpeitao', type='boolean', string="Project Is City"),
        'project_begin_date': fields.related('project_id', 'begin_date', type='date', string="Project Start Date"),


    }
    _sql_constraints = [('contract_num_unique', 'unique(number)', 'number must be unique !')]

    _defaults = {
        'type': 'common',
        'is_import': False,
        'change': u'正常',

    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(updis_contract_contract, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        if not record_id:
            return res

        if 'project_id' in fields:
            res['project_id'] = record_id
        return res

    def _get_project_category_on_change(self, cr, uid, ids, project_id, context=None):
        project = self.pool.get('project.project').browse(cr, uid, project_id, context)
        if project:
            if project.shifoutoubiao:
                return project.toubiaoleibie
            else:
                return project.categories_id.name
        else:
            return ""

    def on_change_project(self, cr, uid, ids, project_id, context=None):
        ret = {'value': {}}
        if project_id:
            project = self.pool.get('project.project').browse(cr, uid, project_id, context)
            values = {
                'name': project.name,
                'project_number': project.xiangmubianhao,
                'number': project.xiangmubianhao,
                'design_department': project.chenjiebumen_id.id if project.chenjiebumen_id else None,
                'project_scale': project.guimo,
                'project_level': project.guanlijibie,
                'customer': project.partner_id and [project.partner_id.id] or [],
                'customer_contact': project.customer_contact and [project.customer_contact.id] or [],
                'project_category': project.categories_id.id if project.categories_id else None,
                'project_is_tender': project.shifoutoubiao,
                'project_tender_type': project.toubiaoleibie,
                'project_is_city': project.shizhenpeitao,
                'project_begin_date': project.begin_date,
            }
            ret['value'].update(values)
        else:
            values = {
                'name': "",
                'project_number': "",
                'number': None,
                'design_department': None,
                'project_scale': "",
                'project_level': "",
                'customer': [],
                'customer_contact': [],
                'project_category': None,
                'project_is_tender': False,
                'project_tender_type': None,
                'project_is_city': False,
                'project_begin_date': None,

            }
            ret['value'].update(values)
        return ret

    def _update_related_contract_id(self, cr, uid, vals, first, second, second_obj, contract_id, context):
        if first in vals.keys():
            for i in vals[first]:
                if len(i) == 3:
                    second_dict = i[2]
                    if second_dict and second in second_dict.keys():
                        for j in second_dict[second]:
                            if len(j) == 3:
                                ids = j[2]
                                self.pool.get(second_obj).write(cr, uid, ids, {'contract_id': contract_id}, context)

    def _update_contract_id(self, cr, uid, vals, contract_id, context):
        self._update_related_contract_id(cr, uid, vals, 'income_ids', 'invoice_ids', 'project.contract.invoice',
                                         contract_id, context)
        self._update_related_contract_id(cr, uid, vals, 'invoice_ids', 'income_ids', 'project.contract.income',
                                         contract_id, context)

    def create(self, cr, uid, vals, context=None):
        mid = super(updis_contract_contract, self).create(cr, uid, vals, context)
        self._update_contract_id(cr, uid, vals, mid, context)
        return mid

    def write(self, cr, uid, ids, vals, context=None):
        if len(ids) == 1:
            self._update_contract_id(cr, uid, vals, ids[0], context)
        result = super(updis_contract_contract, self).write(cr, uid, ids, vals, context=context)
        return result

    def all_contract_action(self, cr, uid, context=None):
        domain = []
        if self.user_has_groups(cr, uid, 'up_contract.group_up_contract_partial_user', context=context):
            hr_id = self.pool.get('hr.employee').search(cr, uid, [("user_id", '=', uid)], context=context)
            if hr_id:
                hr_record = self.pool.get('hr.employee').browse(cr, uid, hr_id[0], context=context)
                user_department_id = hr_record.department_id.id if hr_record.department_id else 0
                domain = [('design_department.id', '=', user_department_id)]
            else:
                domain = [('design_department.id', '=', 0)]
        if self.user_has_groups(cr, uid, 'up_contract.group_up_contract_user', context=context):
            domain = []

        context['search_default_is-common-contract'] = 1
        return {
            'name': u'所有合同',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'project.contract.contract',
            'target': 'current',
            'domain': domain,
            'context': context,
        }

    def third_party_contract_action(self, cr, uid, context=None):
        domain = []
        if self.user_has_groups(cr, uid, 'up_contract.group_up_contract_partial_user', context=context):
            hr_id = self.pool.get('hr.employee').search(cr, uid, [("user_id", '=', uid)], context=context)
            if hr_id:
                hr_record = self.pool.get('hr.employee').browse(cr, uid, hr_id[0], context=context)
                user_department_id = hr_record.department_id.id if hr_record.department_id else 0
                domain = [('design_department.id', '=', user_department_id)]
            else:
                domain = [('design_department.id', '=', 0)]
        if self.user_has_groups(cr, uid, 'up_contract.group_up_contract_user', context=context):
            domain = []
        context['search_default_is-third-party-contract'] = 1
        return {
            'name': u'所有合同',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'project.contract.contract',
            'target': 'current',
            'domain': domain,
            'context': context,
        }


class updis_project_project(osv.osv):
    _inherit = "project.project"
    _name = 'project.project'

    def _is_user_contract_visible(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = False
            if uid in [u.id for u in obj.user_id]:
                result[obj.id] = True
            elif self.user_has_groups(cr, uid,
                                      'up_contract.group_up_contract_user,up_contract.group_up_contract_manager,up_contract.group_up_contract_admin',
                                      context=context):
                result[obj.id] = True

            else:
                hr_id = self.pool.get('hr.employee').search(cr, uid, [("user_id", '=', uid)], context=context)
                if hr_id:
                    hr_record = self.pool.get('hr.employee').browse(cr, uid, hr_id[0], context=context)
                    user_department_id = hr_record.department_id.id if hr_record.department_id else "sdfsdf"
                    project_department_id = obj.chenjiebumen_id.id if obj.chenjiebumen_id else None
                    if user_department_id == project_department_id and self.user_has_groups(cr, uid,
                                                                                            'up_project.group_up_project_suozhang',
                                                                                            context=context):
                        result[obj.id] = True
        return result

    _columns = {
        'contract_ids': fields.one2many('project.contract.contract', 'project_id',
                                        string='Project Contracts'),
        'can_see_contract': fields.function(_is_user_contract_visible, type="boolean",
                                            string="Is User Can See Contract"),
    }


class project_active_tasking_inherit(osv.osv):
    _name = "project.project.active.tasking"
    _inherit = "project.project.active.tasking"

    def workflow_manager_room(self, cr, uid, ids, context=None):
        contract_obj = self.pool.get("project.contract.contract")
        project = self.browse(cr, uid, ids[0], context=context)
        if project and not project.is_import:
            cid = contract_obj.create(cr, 1, {"name": project.name, 'project_id': project.project_id.id,
                                              "number": project.xiangmubianhao,
                                              "customer": [
                                                  (6, 0, [project.partner_id.id] if project.partner_id else [])],
                                              "customer_contact": [(6, 0, [
                                                  project.customer_contact.id] if project.customer_contact else [])]},
                                      context=context)
        tasking = self.browse(cr, 1, ids[0], context=context)
        if not tasking.is_import:
            self.write(cr, 1, ids, {'state': 'end', 'status_code': 10106, 'begin_date': datetime.date.today()},
                       context=context)
        else:
            self.write(cr, 1, ids, {'state': 'end', 'status_code': 10106, },
                       context=context)

        return True