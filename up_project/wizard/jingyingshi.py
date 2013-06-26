# -*- coding: utf-8 -*-
import datetime
from osv import osv, fields


class jingyingshishenpi_form(osv.osv):
    """经营室审批单"""
    _name = "project.review.jingyingshishenpi.form"
    _description = u"经营室审批"
    _inherit = ['project.review.abstract']
    _columns = {
        "xiangmubianhao": fields.char(u"项目编号", select=True, size=128, ),
        "pingshenfangshi": fields.selection([(u'会议', u'会议'), (u'会签', u'会签'), (u'审批', u'审批')], u"评审方式"),
        "yinfacuoshi": fields.selection([(u'可以接受', u'可以接受'), (u'不接受', u'不接受'), (u'加班', u'加班'),
                                         (u'院内调配', u'院内调配'), (u'外协', u'外协'), (u'其它', u'其它')], u"引发措施记录"),
        "renwuyaoqiu": fields.selection([(u'见委托书', u'见委托书'), (u'见合同草案', u'见合同草案'), (u'见洽谈记录', u'见洽谈记录'),
                                         (u'见电话记录', u'见电话记录'), (u'招标文件', u'招标文件')], u"任务要求"),
        "chenjiebumen_id": fields.many2one("hr.department", u"承接部门"),
    }
    _defaults = {
    }

    _sql_constraints = [('xiangmubianhao_uniq', 'unique(xiangmubianhao)', 'xiangmubianhao must be unique !')]

    def jingyinshi_review_submit(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'submitter_id': uid})
        project = self.pool.get('project.project')
        current_record = self.browse(cr, uid, ids, context=context)

        # for record in current_record:
        #     if record.chenjiebumen_id:
        #         hr_department = self.pool.get('hr.department')
        #         department_sequence = hr_department.browse(cr, 1, record.chenjiebumen_id.id,
        #                                                    context=context).project_sequence
        #         department_sequence += 1
        #         hr_department.write(cr, 1, record.chenjiebumen_id.id,
        #                             {'project_sequence': department_sequence})

        if current_record and current_record[0].project_id:
            project.write(cr, uid, current_record[0].project_id.id,
                          {'project_logs': [(0, 0, {'project_id': current_record[0].project_id.id,
                                                    'log_user': uid,
                                                    'log_info': u'经营室审批通过,提交申请到总师室'})]})
            project._workflow_signal(cr, uid, [current_record[0].project_id.id], 'jingyinshi_submit')
            return True
        else:
            return False

    def on_change_department(self, cr, uid, ids, department_id, context=None):
        ret = {'value': {}}
        if department_id:
            department = self.pool.get('hr.department').browse(cr, uid, department_id)

            department_code = department.code
            department_sequence = department.project_sequence
            year = datetime.date.today().year
            jinyinshi = self.browse(cr, uid, ids, context=context)
            if jinyinshi:
                is_tender = jinyinshi[0].project_id.suozhangshenpi_form_id.shifoutoubiao
            else:
                is_tender = False
            project_num = "%d%s%s%d" % (year, (is_tender and "T" or ""), department_code, department_sequence)
            sms_vals = {
                'xiangmubianhao': project_num,
            }
            ret['value'].update(sms_vals)
        return ret


class updis_project(osv.Model):
    _inherit = 'project.project'
    _columns = {
        'jingyingshishenpi_form_id': fields.many2one('project.review.jingyingshishenpi.form', u'经营室审批单',
                                                     ondelete="cascade", ),

        "xiangmubianhao": fields.related('jingyingshishenpi_form_id', 'xiangmubianhao', type="char",
                                         string=u"项目编号"),
        "pingshenfangshi": fields.related('jingyingshishenpi_form_id', 'pingshenfangshi', type="char",
                                          string=u"评审方式"),
        "yinfacuoshi": fields.related('jingyingshishenpi_form_id', 'yinfacuoshi', type="char",
                                      string=u"引发措施记录"),
        "renwuyaoqiu": fields.related('jingyingshishenpi_form_id', 'renwuyaoqiu', type="char",
                                      string=u"任务要求"),
        "chenjiebumen_id": fields.related('jingyingshishenpi_form_id', 'chenjiebumen_id', type="many2one",
                                          relation="hr.department",
                                          string=u"承接部门"),
        "jinyinshi_submitter_id": fields.related('jingyingshishenpi_form_id', 'submitter_id', type="many2one",
                                                 relation="res.users",
                                                 string=u"Submitter"),
    }

    def action_jingyingshishenpi(self, cr, uid, ids, context=None):
        return self._get_action(cr, uid, ids, 'project.review.jingyingshishenpi.form', u'经营室审批单')

    def init_jinyinshi_form(self, cr, uid, ids, state, obj, object_field):
        assert len(ids) == 1
        project_id = self.browse(cr, uid, ids, context=None)
        if project_id[0] and project_id[0].suozhangshenpi_form_id:
            department_id = project_id[0].suozhangshenpi_form_id.jianyishejibumen_id.id
            is_tender = project_id[0].suozhangshenpi_form_id.shifoutoubiao
        else:
            department_id = None
            is_tender = False

        if project_id[0] and project_id[0][object_field]:
            jinyishi = self.pool.get(obj)
            jinyishi_id = jinyishi.write(cr, 1, project_id[0].jingyingshishenpi_form_id.id,
                                         {'chenjiebumen_id': department_id})
            self.write(cr, uid, ids, {'state': state})
            return project_id[0][object_field].id
        else:
            if department_id:
                department_code = project_id[0].suozhangshenpi_form_id.jianyishejibumen_id.code
                department_sequence = project_id[0].suozhangshenpi_form_id.jianyishejibumen_id.project_sequence
                year = datetime.date.today().year
                if department_code:
                    project_num = "%d%s%s%d" % (year, (is_tender and "T" or ""), department_code, department_sequence)
                    department_sequence += 1
                    self.pool.get('hr.department').write(cr, 1, department_id,
                                                         {'project_sequence': department_sequence})
                else:
                    project_num = None
            else:
                project_num = None
            suozhangshenpi = self.pool.get(obj)
            suozhangshenpi_id = suozhangshenpi.create(cr, 1,
                                                      {'project_id': ids[0], 'xiangmubianhao': project_num,
                                                       'chenjiebumen_id': department_id},
                                                      None)
            self.write(cr, uid, ids, {'state': state, object_field: suozhangshenpi_id})
            return suozhangshenpi_id

    def suozhangshenpi_reject(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids,
                   {'project_logs': [(0, 0, {'project_id': ids,
                                             'log_user': uid,
                                             'log_info': u'经营室打回申请单'})]})
        self._workflow_signal(cr, uid, ids, 'suozhangshenpi_reject')
        return True