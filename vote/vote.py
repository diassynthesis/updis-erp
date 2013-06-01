__author__ = 'cysnake4713'
from openerp import tools

from osv import osv, fields


class VoteCategory(osv.osv):
    _name = "updis.vote"
    _description = 'UPDIS Vote Category'
    _order = "name"
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
    }


_defaults = {
    'allow_vote_time': 1,
    'is_display': False,
    'have_image': False,
}


class VoteRecord(osv.osv):
    _name = "updis.vote.record"
    _description = 'UPDIS Vote Record'

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


    _columns = {
        'name': fields.char(size=100, required=True, string="Vote Record Name"),
        'vote_category': fields.many2one('updis.vote', string='Vote Category', required=True),
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
        'vote_logs': fields.one2many('updis.vote.log', 'vote_record', "Vote History"),
    }

    _defaults = {
        'have_image': False,
    }


class VoteLog(osv.osv):
    _name = "updis.vote.log"
    _description = 'UPDIS Vote Log'
    _columns = {
        'voter': fields.many2one('res.users', string='Voter'),
        'vote_record': fields.many2one('updis.vote.record', string='Vote record'),
        'vote_time': fields.datetime('Vote Time'),
    }

