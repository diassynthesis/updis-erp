# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# coding=utf-8
from openerp import tools
from openerp import models, fields, api
from openerp.tools.translate import _


class report_project_task_user(models.Model):
    _name = "report.project.project.analysis"
    _auto = False
    _order = 'id desc'

    nbr = fields.Integer('# of Projects', readonly=True)
    name = fields.Char('Project Name', readonly=True)
    start_date = fields.Date('Start Date', readonly=True)
    end_date = fields.Date('End Date', readonly=True)
    state = fields.Selection([("project_active", u"Project Active"),
                              ("project_cancelled", u"Project Cancelled"),
                              ("project_processing", u"Project Processing"),
                              ("project_stop", u"Project Stop"),
                              ("project_pause", u"Project Pause"),
                              ("project_filed", u"Project Filing"),
                              ("project_finish", u"Project Filed"),
                              ("project_process_cancel", u"Project Cancelled in Processing"),
                             ], 'State', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Customers', readonly=True)
    remaining_days = fields.Float('Remaining Days', digits=(16, 2), readonly=True)
    project_type = fields.Many2one("project.type", string="Project Type", readonly=True)
    state_id = fields.Many2one('res.country.state', string='Province', readonly=True)

    chenjiebumen_id = fields.Many2one("hr.department", u"In Charge Department", readonly=True)
    categories_id = fields.Many2one("project.upcategory", u"项目类别", readonly=True)
    guanlijibie = fields.Selection([('LH200307240001', u'院级'), ('LH200307240002', u'所级')], u'Project Level', readonly=True)
    partner_type = fields.Selection([("WT200508180001", u"深圳规划局"),
                                     ("WT200508180002", u"深圳市其他"),
                                     ("WT200508180003", u"市外"),
                                     ("WT200509020001", u"其它"), ], string="Partner Type", readonly=True)
    plan_finish_date = fields.Date(string='Plan Finish Date')
    city_type = fields.Selection([('CC200511210001', u'直辖市'), ('CC200511210002', u'省会城市'), ('CC200511210003', u'地级市'),
                                  ('CC200511210004', u'县级市'), ('CC200511210005', u'其它'), ('plan_city', u'计划单列市')], string="City Type", readonly=True)

    @api.cr
    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'report_project_project_analysis')
        cr.execute("""
            CREATE view report_project_project_analysis as
              SELECT
                    (select 1 ) AS nbr,
                    p.id as id,
                    a.name as name,
                    p.begin_date as start_date,
                    p.filed_project_end_date as end_date,
                    p.state as state,
                    a.partner_id as partner_id,
                    p.project_type as project_type,
                    p.state_id as state_id,
                    p.chenjiebumen_id as chenjiebumen_id,
                    p.categories_id as categories_id,
                    p.partner_type as partner_type,
                    p.plan_finish_date as plan_finish_date,
                    p.city_type as city_type,
                    p.guanlijibie as guanlijibie,
                    (extract('epoch' from (COALESCE(p.filed_project_end_date, (now() at time zone 'UTC')) - p.begin_date)))/(3600*24)  as remaining_days
              FROM project_project as p
              INNER JOIN account_analytic_account as a on p.analytic_account_id = a.id
                GROUP BY
                    p.id,
                    name,
                    start_date,
                    p.state,
                    partner_id,
                    project_type,
                    state_id,
                    chenjiebumen_id,
                    categories_id,
                    partner_type,
                    plan_finish_date,
                    city_type,
                    end_date,
                    guanlijibie,
                    remaining_days
        """)
