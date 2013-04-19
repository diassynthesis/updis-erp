from osv import osv, fields


class res_users(osv.osv):
    _inherit = "res.users"
    _columns = {
        'sign_image': fields.binary("Sign Image",
                                    help="This field holds the image used as siganture for this contact"),
        'address_id': fields.many2one('res.partner', 'Working Address'),
        'work_email': fields.char('Work Email', size=240),
        'work_phone': fields.char('Work Phone', size=32, readonly=False),
        'mobile_phone': fields.char('Work Mobile', size=32, readonly=False),
        'work_location': fields.char('Office Location', size=32),
        'interest': fields.char("Interest", size=100),
        'practice': fields.text("Practice"),
        'person_resume': fields.text("Personal Resume"),
        'home_phone': fields.char('Home Phone', size=32, readonly=False),


    }

    SELF_WRITEABLE_FIELDS = ['password', 'signature', 'action_id', 'company_id', 'email', 'name', 'image',
                             'image_medium', 'image_small', 'lang', 'tz', 'address_id', 'work_email', 'work_phone',
                             'mobile_phone', 'work_location', 'interest', 'practice', 'person_resume', 'home_phone']

