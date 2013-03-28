from osv import fields, osv
from openerp import tools


class updis_department(osv.osv):
    _description = "UPDIS Department"
    _inherit = "hr.department"

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value), 'have_image': True}, context=context)

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
                                        string="Medium-sized photo", type="binary", multi="_get_image",
                                        store={
                                            'hr.department': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                        },
                                        help="Medium-sized photo of the employee. It is automatically " \
                                             "resized as a 128x128px image, with aspect ratio preserved. " \
                                             "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
                                       string="Smal-sized photo", type="binary", multi="_get_image",
                                       store={
                                           'hr.department': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                       },
                                       help="Small-sized photo of the employee. It is automatically " \
                                            "resized as a 64x64px image, with aspect ratio preserved. " \
                                            "Use this field anywhere a small image is required."),
    }
    _defaults = {
        "deleted": 0,
        'sequence': 10,
        'display_in_front': True,
        'is_in_use': True,
        'have_image': False,
    }
    _order = 'sequence,id'


updis_department()
