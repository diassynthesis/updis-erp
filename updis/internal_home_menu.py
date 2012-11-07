from osv import osv,fields
from openerp import SUPERUSER_ID

class internal_home_menu(osv.osv):
	_name = "internal.home.menu"
	_inherit = "ir.ui.menu"
	_columns = {	
		'child_id' : fields.one2many('internal.home.menu', 'parent_id','Child IDs'),
		'parent_id': fields.many2one('internal.home.menu', 'Parent Menu', select=True),
	}
	def _filter_visible_menus(self, cr, uid, ids, context=None):
		"""Filters the give menu ids to only keep the menu items that should be
		   visible in the menu hierarchy of the current user.
		   Uses a cache for speeding up the computation.
		"""
		with self.cache_lock:
			modelaccess = self.pool.get('ir.model.access')
			user_groups = set(self.pool.get('res.users').read(cr, SUPERUSER_ID, uid, ['groups_id'])['groups_id'])
			result = []
			for menu in self.browse(cr, uid, ids, context=context):
				# this key works because user access rights are all based on user's groups (cfr ir_model_access.check)
				key = (cr.dbname, menu.id, tuple(user_groups))
				if key in self._cache:
					if self._cache[key]:
						result.append(menu.id)
					#elif not menu.groups_id and not menu.action:
					#    result.append(menu.id)
					continue

				self._cache[key] = False
				if menu.groups_id:
					restrict_to_groups = [g.id for g in menu.groups_id]
					if not user_groups.intersection(restrict_to_groups):
						continue
					#result.append(menu.id)
					#self._cache[key] = True
					#continue

				if menu.action:
					# we check if the user has access to the action of the menu
					data = menu.action
					if data:
						model_field = { 'ir.actions.act_window':    'res_model',
										'ir.actions.report.xml':    'model',
										'ir.actions.wizard':        'model',
										'ir.actions.server':        'model_id',
									  }

						field = model_field.get(menu.action._name)
						if field and data[field]:
							if not modelaccess.check(cr, uid, data[field], 'read', False):
								continue
				# else:
				#     # if there is no action, it's a 'folder' menu
				#     if not menu.child_id:
				#         # not displayed if there is no children
				#         continue

				result.append(menu.id)
				self._cache[key] = True
			return result