# -*- encoding:utf-8 -*-
import openerp
from openerp.osv import osv, fields
from up_contract import contract_tools

__author__ = 'cysnake4713'


class up_contract_analysis(osv.osv):
    _name = "project.contract.contract.analysis"
    _description = "Project Contract Analysis"
    _auto = False
    _rec_name = "contract_name"
    _order = "contract_id desc"
    _columns = {
        'contract_id': fields.many2one('project.contract.contract', 'Contract', readonly=1),
        'contract_name': fields.related('contract_id', 'name', type="char",
                                        string="Contract Name", readonly=1),
        'department_id': fields.related('contract_id', 'design_department', relation='hr.department', type="many2one",
                                        string="Design Department", readonly=1),
        'contract_num': fields.related('contract_id', 'number', type="char",
                                       string="Contract Num", readonly=1),
        'contract_entrust_type': fields.related('contract_id', 'entrust_type', type="selection",
                                                selection=[('WT200508180001', u'深圳规划局'), ('WT200508180002', u"深圳市其他"),
                                                           ('WT200508180003', u"市外"),
                                                           ('WT200509020001', u"其他")]
            , readonly=1, string="Entrust Type"),
        'contract_sign_date': fields.date(string="Sign Date"),

        'project_id': fields.related('contract_id', 'project_id', type="many2one", relation='project.project',
                                     string="Project", readonly=1),
        'project_manager': fields.related('project_id', 'user_id', type="many2many", relation='res.users',
                                          string="Project Manager", readonly=1),
        'project_category': fields.related('project_id', 'categories_id', type="many2one",
                                           relation='project.upcategory',
                                           string="Project Category", readonly=1),
        'project_state': fields.related('project_id', 'state', type="selection",
                                        selection=[("project_active", u"Project Active"),
                                                   ("project_cancelled", u"Project Cancelled"),
                                                   ("project_processing", u"Project Processing"),
                                                   ("project_stop", u"Project Stop"),
                                                   ("project_pause", u"Project Pause"),
                                                   ("project_filed", u"Project Filing"),
                                                   ("project_finish", u"Project Filed"),
                                        ],
                                        string="Project State", readonly=1),
        'total_price': fields.float(string='Total Price', digits=(16, 6), readonly=1),
        'paid_price': fields.float(string='Paid Price', digits=(16, 6), readonly=1),
        'remain_price': fields.float(string='Remain Price', digits=(16, 6), readonly=1),
        'customer': fields.related('contract_id', 'customer', type="many2many",
                                   relation='res.partner',
                                   string="Contract Customer", readonly=1),
    }

    def init(self, cr):
        openerp.tools.sql.drop_view_if_exists(cr, 'project_contract_contract_analysis')
        cr.execute(" CREATE VIEW project_contract_contract_analysis AS ( "
                   " SELECT "
                   " c.id as id,"
                   " c.id as contract_id,"
                   " COALESCE(c.price, 0.0) as total_price,"
                   " COALESCE(SUM(i.price), 0.0) as paid_price,"
                   " COALESCE(c.price, 0.0) - COALESCE(SUM(i.price), 0.0) as remain_price,"
                   " to_char(c.sign_date, 'YYYY-MM-DD') AS contract_sign_date"
                   " FROM "
                   " project_contract_contract as c LEFT JOIN project_contract_income as i"
                   " on c.id = i.contract_id"
                   " WHERE c.type = 'common' "
                   " GROUP BY c.id"
                   " )")

    def all_contract_analysis_action(self, cr, uid, context=None):
        if self.user_has_groups(cr, uid, 'up_contract.group_up_contract_all_limit', context=context):
            domain = []
        else:
            user_department_id = contract_tools.get_user_department(self, cr, uid, context)
            domain = [('department_id.id', '=', user_department_id)]
        return {
            'name': u'收费进度查询',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'project.contract.contract.analysis',
            'target': 'current',
            'domain': domain,
            'context': context,
        }
