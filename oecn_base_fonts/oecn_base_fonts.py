# -*- encoding: utf-8 -*-
# __author__ = jeff@openerp.cn
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from reportlab.lib.styles import ParagraphStyle
from osv import osv
from tools.safe_eval import safe_eval as eval
import os

# make this module compaitible with V6.1 and lower
try:
    import openerp.report.render.rml2pdf.customfonts as cfonts
except ImportError:
    import report.render.rml2pdf.customfonts as cfonts
try:
    from openerp import SUPERUSER_ID
except ImportError:
    SUPERUSER_ID = 1

class oecn_base_fonts(osv.osv_memory):
    _name = "oecn.base.fonts"
    _description = "Register system fonts to replace pdf fonts"
    def __init__( self, pool, cr ):
        super(osv.osv_memory, self).__init__(pool, cr)
        config_obj = pool.get("ir.config_parameter")
        maps = config_obj.get_param(cr, SUPERUSER_ID, 'fonts_map')        
        if maps:
            mappings = eval(maps)
            for m in mappings['maps']:
                if not os.path.exists(m[2]):
                    ids = config_obj.search(cr, SUPERUSER_ID, [('key','=','fonts_map')])
                    config_obj.unlink(cr, SUPERUSER_ID, ids) 
                    break            
            cfonts.CustomTTFonts = mappings['maps']
            if mappings['wrap']:
                ParagraphStyle.defaults['wordWrap'] = 'CJK'

oecn_base_fonts()
