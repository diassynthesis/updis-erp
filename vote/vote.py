from datetime import datetime

__author__ = 'cysnake4713'
from openerp import tools

from openerp.osv import osv, fields


class VoteCategory(osv.osv):
    _name = "updis.vote"
    _description = 'UPDIS Vote Category'
    _order = "id desc"
    _log_access = True

    def _image_resize_image_fixed(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            return_dict = dict()
            return_dict['image_fixed'] = tools.image_resize_image_medium(obj.image, size=(435, 232))
            result[obj.id] = return_dict

        return result

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result


    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value), 'have_image': True},
                          context=context)


    _columns = {
        'name': fields.char(size=100, required=True, string="Vote Name"),
        'description': fields.char(size=256, string='Vote Description'),
        'is_display': fields.boolean('Vote is display in cms?'),
        'start_time': fields.date(string="Vote Start Time", required=True),
        'end_time': fields.date(string='Vote End Time', required=True),
        'allow_vote_time': fields.integer(string="Each one allowed vote times", required=True),
        'have_image': fields.boolean("is vote photo upload"),
        'image': fields.binary("Vote Category Photo Basic",
                               help="This field holds the image used as photo for the vote, limited to 435*232px."),
        'image_fixed': fields.function(_image_resize_image_fixed, fnct_inv=_set_image, string="Vote Category Photo",
                                       type="binary", multi="_get_image",
                                       store={
                                           'updis.vote': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                       }),
        'vote_logs': fields.one2many('updis.vote.log', 'vote_category', "Vote History"),
        'comment': fields.text(string='Vote Comment'),
        'vote_record_ids': fields.one2many('updis.vote.record', 'vote_category', string="Related Records"),
        'show_result': fields.boolean(string='Showing Result in CMS?'),
    }

    _defaults = {
        'allow_vote_time': 1,
        'is_display': False,
        'have_image': False,
    }


class VoteRecord(osv.osv):
    _name = "updis.vote.record"
    _description = 'UPDIS Vote Record'
    _inherit = ['mail.thread']

    def _image_resize_image_fixed(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            return_dict = dict()
            return_dict['record_image'] = tools.image_resize_image_medium(obj.image, size=(275, 145))
            result[obj.id] = return_dict

        return result

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result


    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value), 'have_image': True},
                          context=context)

    def _get_vote_number(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.vote_logs:
                vote_logs_total = len(obj.vote_logs)
                result[obj.id] = vote_logs_total
            else:
                result[obj.id] = 0
        return result


    _columns = {
        'name': fields.char(size=100, required=True, string="Vote Record Name"),
        'vote_category': fields.many2one('updis.vote', string='Vote Category', required=True, ondelete="cascade"),
        'author': fields.many2one('hr.employee', string='Author'),
        'have_image': fields.boolean("is vote record photo upload"),
        'image': fields.binary("Vote Record Photo Basic",
                               help="This field holds the image used as photo for the vote record, limited to 275*145px."),
        'record_image': fields.function(_image_resize_image_fixed, fnct_inv=_set_image, string="Vote Record Photo",
                                        type="binary", multi="_get_image",
                                        store={
                                            'updis.vote.record': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                        }),
        'content': fields.text("Content"),
        'description': fields.char(size=256, string='Vote Record Description'),
        'vote_logs': fields.many2many("updis.vote.log", "vote_log_vote_record_rel",
                                      "vote_record_id", "vote_log_id",
                                      string='Vote Logs'),
        'vote_number': fields.function(_get_vote_number, type='integer', string="Get Vote Number",
                                       readonly=True)
    }

    _defaults = {
        'have_image': False,
    }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {'mail_create_nolog': True}
        else:
            context.update({'mail_create_nolog': True})
        return super(VoteRecord, self).create(cr, uid, vals, context)


class VoteLog(osv.osv):
    _name = "updis.vote.log"
    _description = 'UPDIS Vote Log'
    _columns = {
        'voter': fields.many2one('res.users', string='Voter'),
        'vote_category': fields.many2one('updis.vote', string='Vote Category', ondelete="cascade"),
        'vote_time': fields.datetime('Vote Time'),
        'vote_for': fields.many2many("updis.vote.record", "vote_log_vote_record_rel",
                                     "vote_log_id", "vote_record_id",
                                     string='Vote For'),
    }

    _defaults = {
        'vote_time': lambda *a: datetime.now(),
    }

    #TODO:add create previllage

