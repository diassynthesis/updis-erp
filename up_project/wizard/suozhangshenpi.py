# -*- coding: utf-8 -*-

from osv import osv, fields


class suozhangshenpi_form(osv.osv):
    """所长审批单"""
    _name = "project.review.suozhangshenpi.form"
    _description = u"所长审批任意人员提交的申请单"
    _inherit = ['project.review.abstract']
    _columns = {
        "yaoqiuxingchengwenjian": fields.selection([
                                                       (u"已形成", u"已形成"),
                                                       (u"未形成，但已确认", u"未形成，但已确认")],
                                                   u"顾客要求形成文件否"),
        # 所长审批
        "express_requirement": fields.selection([(u"有招标书", u"有招标书"), (u"有委托书", u"有委托书"),
                                                 (u"有协议/合同草案", u"有协议/合同草案"), (u"有口头要求记录", u"有口头要求记录")],
                                                string="Express Requirement"),

        "yinhanyaoqiu": fields.selection([(u"有", u"有（需在评审记录一栏中标明记录）"), (u"无", u"无")], u"隐含要求"),
        "difangfagui": fields.selection([(u"有", u"有（需在评审记录一栏中标明记录）"), (u"无", u"无")], u"地方规范或特殊法律法规", ),
        "fujiayaoqiu": fields.selection([(u"有", u"有（需在评审记录一栏中标明记录）"), (u"无", u"无")], u"附加要求", ),
        "hetongyizhi": fields.selection([(u"合同/协议要求表述不一致已解决", u"合同/协议要求表述不一致已解决"),
                                         (u"没有出现不一致", u"没有出现不一致")], u"不一致是否解决", ),
        "ziyuan": fields.selection([(u'人力资源满足', u'人力资源满足'), (u'人力资源不足', u'人力资源不足')], u'人力资源', ),
        #本院是否有能力满足规定要求
        "shebei": fields.selection([(u'设备满足', '设备满足'), (u'设备不满足', u'设备不满足')], u"设备", ), #本院是否有能力满足规定要求
        "gongqi": fields.selection([(u'工期可接受', '工期可接受'), (u'工期太紧', u'工期太紧')], u"工期", ), #本院是否有能力满足规定要求
        "shejifei": fields.selection([(u'设计费合理', '设计费合理'), (u'设计费太低', u'设计费太低')], u'设计费', ), #本院是否有能力满足规定要求
        "state": fields.related('project_id', 'state', type="char", string="State"),


        # basic
        "waibao": fields.boolean(u"是否外包"),
        "shizhenpeitao": fields.boolean(u"市政配套"),
        "duofanghetong": fields.boolean(u"多方合同"),
        "jianyishejibumen_id": fields.many2one("hr.department", u"建议设计部门"),
        "jianyixiangmufuzeren_id": fields.many2one("hr.employee", u"建议项目负责人"),
        "shifoutoubiao": fields.boolean(u"是否投标项目"),
        "toubiaoleibie": fields.selection([(u'商务标', u'商务标'), (u'技术标', u'技术标'), (u'综合标', u'综合标')], u"投标类别"),
    }

    def onchange_shifoutoubiao(self, cr, uid, ids, shifoutoubiao, context=None):
        # if shifoutoubiao:
        return {'value': {}}

    def suozhangshenpi_review_submit(self, cr, uid, ids, context=None):
        project = self.pool.get('project.project')
        suozhangshenpi = self.browse(cr, uid, ids, context=None)
        if suozhangshenpi and suozhangshenpi[0].project_id:
            project._workflow_signal(cr, uid, [suozhangshenpi[0].project_id.id], 'draft_submit')
            return True
        else:
            return False

    def suozhangshenpi_review_accept(self, cr, uid, ids, context=None):
        project = self.pool.get('project.project')
        suozhangshenpi = self.browse(cr, uid, ids, context=None)
        if suozhangshenpi and suozhangshenpi[0].project_id:
            project._workflow_signal(cr, uid, [suozhangshenpi[0].project_id.id], 'suozhangshenpi_submit')
            return True
        else:
            return False


class updis_project(osv.osv):
    _inherit = 'project.project'

    def _is_display_button(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            review_id = obj.suozhangshenpi_form_id.reviewer_id.id
            if review_id == uid:
                result[obj.id] = True
            else:
                result[obj.id] = False
        return result

    _columns = {
        'suozhangshenpi_form_id': fields.many2one('project.review.suozhangshenpi.form', u'所长审批单'),


        "yaoqiuxingchengwenjian": fields.related('suozhangshenpi_form_id', 'yaoqiuxingchengwenjian', type="char",
                                                 string=u"顾客要求形成文件否"),
        # 所长审批
        "express_requirement": fields.related('suozhangshenpi_form_id', 'express_requirement', type="char",
                                              string="Express Requirement"),
        "yinhanyaoqiu": fields.related('suozhangshenpi_form_id', 'yinhanyaoqiu', type="char", string=u"隐含要求"),
        "difangfagui": fields.related('suozhangshenpi_form_id', 'difangfagui', type="char", string=u"地方规范或特殊法律法规"),
        "fujiayaoqiu": fields.related('suozhangshenpi_form_id', 'fujiayaoqiu', type="char", string=u"附加要求"),
        "hetongyizhi": fields.related('suozhangshenpi_form_id', 'hetongyizhi', type="char",
                                      string=u"合同/协议要求表述不一致已解决"),
        "ziyuan": fields.related('suozhangshenpi_form_id', 'ziyuan', type="char", string=u'人力资源'),
        #本院是否有能力满足规定要求
        "shebei": fields.related('suozhangshenpi_form_id', 'shebei', type="char", string=u"设备"),
        "gongqi": fields.related('suozhangshenpi_form_id', 'gongqi', type="char", string=u"工期"),
        "shejifei": fields.related('suozhangshenpi_form_id', 'shejifei', type="char", string=u'设计费'),

        # basic
        "waibao": fields.related('suozhangshenpi_form_id', 'waibao', type="boolean", string=u'是否外包'),
        "shizhenpeitao": fields.related('suozhangshenpi_form_id', 'shizhenpeitao', type="boolean", string=u'市政配套'),
        "duofanghetong": fields.related('suozhangshenpi_form_id', 'duofanghetong', type="boolean", string=u'多方合同'),
        "jianyishejibumen_id": fields.related('suozhangshenpi_form_id', 'jianyishejibumen_id', type="many2one",
                                              relation="hr.department",
                                              string=u'建议设计部门'),
        "jianyixiangmufuzeren_id": fields.related('suozhangshenpi_form_id', 'jianyixiangmufuzeren_id', type="many2one",
                                                  relation="hr.employee", string=u'建议项目负责人'),
        "shifoutoubiao": fields.related('suozhangshenpi_form_id', 'shifoutoubiao', type="boolean", string=u'是否投标项目'),
        "toubiaoleibie": fields.related('suozhangshenpi_form_id', 'toubiaoleibie', type="char", string=u'投标类别'),

        'is_display_button': fields.function(_is_display_button, type="boolean",
                                             string="Is Display Button"),
    }

    def action_suozhangshenpi(self, cr, uid, ids, context=None):
        return self._get_action(cr, uid, ids, 'project.review.suozhangshenpi.form', u'所长审批单')
