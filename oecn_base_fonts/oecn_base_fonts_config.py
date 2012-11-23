# -*- coding: utf-8 -*-
# __author__ = jeff@openerp.cn,joshua@openerp.cn
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

from osv import fields, osv
from reportlab.lib.fontfinder import FontFinder
from reportlab import rl_config
import re
from tools.safe_eval import safe_eval as eval
#patch for ReportLab
import reportlab_patch
RMLS = ['rml_header','rml_header2','rml_header3']
OE_FONTS = ['Helvetica','DejaVuSans','Times','Times-Roman','Courier']

class oecn_base_fonts_map(osv.osv_memory):
    _name = 'oecn_base_fonts.map'

    # try to get the font from the cache first (system_fonts)
    system_fonts = []
    def get_system_fonts(self, cr, uid, context=None):
        if self.system_fonts:
            return self.system_fonts
        else:
            return self._system_fonts_get(cr, uid)
        
    def _system_fonts_get(self, cr, uid, context = None):
        ''' get fonts list on server '''
        # consider both windows and unix like systems
        # get all folders under fonts/ directory
        res = []
        ff = FontFinder( useCache = False )
        fontdirs = rl_config.TTFSearchPath[:] + rl_config.T1SearchPath[:] + rl_config.CMapSearchPath[:]        
        ff.addDirectories(set(fontdirs))
        ff.search()
        for familyName in ff.getFamilyNames():
            for font in ff.getFontsInFamily(familyName):
                if font.fileName[-4:].lower() in (".ttf", ".ttc"):
                    try:
                        fileName = font.fileName.decode('utf-8')
                    except UnicodeDecodeError:
                        fileName = font.fileName.decode('gbk')#for Chinese file name(Windows OS)
                    res.append((fileName, font.name))

        #cache the font list in class variable
        oecn_base_fonts_map.system_fonts = res
        return res

    def _pdf_fonts_get(self, cr, uid, context = None):
        return [('Helvetica','Helvetica'),       \
                ('DejaVuSans','DejaVuSans'),     \
                ('Times','Times'),               \
                ('Times-Roman','Times-Roman'),   \
                ('Courier', 'Courier')]

    _columns = {
        'map_id':fields.many2one('oecn_base_fonts.config','Font Map'),
        'pdf_font':fields.selection(_pdf_fonts_get, 'Original Fonts', required=True),
        'name':fields.char('Font Alias', size=20, required=True, help='use this font alias \
                in custom rml report template'),
        'new_font':fields.selection(get_system_fonts, 'Replaced With', required=True),
    }

    def onchange_new_font(self, cr, uid, ids, new_font):
        """get the default 'Font Alias'"""

        for font_path, font_name in self.system_fonts:
            if new_font == font_path:
                return {'value': {'name': font_name}}

oecn_base_fonts_map()

class oecn_base_fonts_config(osv.osv_memory):
    _name = 'oecn_base_fonts.config'
    _inherit = 'res.config'

    _columns = {
        'wrap':fields.boolean('CJK wrap', required=True, \
            help="If you are using CJK fonts, check this option will wrap your \
            words properly at the edge of the  pdf report"),
        'map_ids':fields.one2many('oecn_base_fonts.map','map_id','Replace Fonts'),
    }

    def _get_wrap(self, cr, uid, *args):
        map = self.pool.get('ir.config_parameter').get_param(cr, 1, 'fonts_map')
        if map:
            return (eval(map)).get('wrap',False)
        return True

    def _get_map_ids(self, cr, uid, *args):
        oecn_map = self.pool.get('ir.config_parameter').get_param(cr, 1, 'fonts_map')
        oecn_map_obj = self.pool.get('oecn_base_fonts.map')
        default_fonts = None, None
        ids = []
        if oecn_map:
            oecn_maps = (eval(oecn_map)).get('maps', False)
            for m in oecn_maps:
                val = {
                    'pdf_font':m[0],
                    'name':m[1],
                    'new_font':m[2],
                    }
                id = oecn_map_obj.create(cr, uid, val)
                ids.append(id)
        elif not oecn_map:
            system_fonts = oecn_map_obj.get_system_fonts(cr, uid)
            for font_path, name, in system_fonts: 
                if name in ('SimHei', 'SimSun','WenQuanYiZenHei'):
                    default_fonts = (font_path, name)
                    break
            for fonts in OE_FONTS:
                val = {
                    'pdf_font':fonts,
                    'name': default_fonts[1] or system_fonts[0][1],
                    'new_font':default_fonts[0] or system_fonts[0][0],
                }
                id = oecn_map_obj.create(cr, uid, val)
                ids.append(id)                    
        return ids

    _defaults = {
        'wrap': _get_wrap,
        'map_ids': _get_map_ids,
    }
    def execute(self, cr, uid, ids, context=None):
        company_obj = self.pool.get('res.company')
        company_ids = company_obj.search(cr, uid, [])
        p = re.compile('<setFont.*(?=size.*)')
        #Replace the font in company rml headrer and footer
        for o in self.browse(cr, uid, ids, context=context):
            config_obj = self.pool.get('ir.config_parameter')
            maps = []
            for map in o.map_ids:
                maps += [(map.pdf_font, map.name ,map.new_font,'all')]
            config_obj.set_param(cr, uid, 'fonts_map', {'wrap':o.wrap,'maps':maps})
            for company in company_obj.read(cr, uid, company_ids, RMLS):
                value = {}
                for rml in RMLS:
                    new_font_rml  = '<setFont name="'+o.map_ids[0].name+'" '
                    value[rml] = p.sub(new_font_rml, company[rml])
                company_obj.write(cr, uid, company['id'], value)
oecn_base_fonts_config()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
