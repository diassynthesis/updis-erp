from openerp import tools

from osv import fields, osv


class updis_department(osv.osv):
    _description = "UPDIS Department"
    _inherit = "hr.department"
    _order = "sequence"

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            return_dict = dict()
            return_dict['image_medium'] = tools.image_resize_image_medium(obj.image, size=(275, 145))
            result[obj.id] = return_dict
        return result

    def _set_image(self, cr, uid, ids, name, value, args, context=None):
        return self.write(cr, uid, [ids], {'image': tools.image_resize_image_big(value, size=(275, 145))},
                          context=context)

    def _has_image(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = obj.image != False
        return result

    _columns = {
        "deleted": fields.boolean("Removed"),
        'is_in_use': fields.boolean('Is in use'),
        'sequence': fields.integer("Display Sequence"),
        'display_in_front': fields.boolean("Display in Front Page"),
        'code': fields.char("Code", size=64),
        'short_name': fields.char('Short name', size=64),
        # image: all image fields are base64 encoded and PIL-supported
        'have_image': fields.boolean("is department photo upload"),
        'image': fields.binary("Department Photo",
                               help="This field holds the image used as photo for the employee, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
                                        string="Medium-sized image", type="binary", multi="_get_image",
                                        store={
                                            'hr.department': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                        }),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
                                       string="Small-sized image", type="binary", multi="_get_image",
                                       store={
                                           'hr.department': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                       }),
        'has_image': fields.function(_has_image, type="boolean", string='Have Image'),
    }

    _defaults = {
        "deleted": 0,
        'sequence': 10,
        'display_in_front': True,
        'is_in_use': True,
        'have_image': False,
    }