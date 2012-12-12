import time
from report import report_sxw

class renwuxiada(report_sxw.rml_parse):
	"""docstring for renwuxiada"""
	def __init__(self, cr,uid,name,context):
		super(renwuxiada,self).__init__(cr,uid,name,context)
		self.localcontext.update({
			'time':time,
			'suozhangshenpi':self._get_suozhangshenpi_form,
			'jingyingshishenpi':self._get_jingyingshishenpi_form,
			'zongshishishenpi':self._get_zongshishishenpi_form,
			'suozhangqianzishenpi':self._get_suozhangqianzishenpi_form,
			'category_names':self._get_category_names,
			})
	def _get_category_names(self,pid):
		# import pdb;pdb.set_trace()
		project = self.pool.get('project.project')
		return [cat.name for cat in project.browse(self.cr,self.uid,pid).categories_id]
	def _get_suozhangshenpi_form(self,pid):
		form = self.pool.get('project.review.suozhangshenpi.form')
		form_ids = form.search(self.cr,self.uid,[('project_id','=',pid),('state','=','accepted')])
		if form_ids:
			return form.browse(self.cr,self.uid,form_ids[0])	
	def _get_jingyingshishenpi_form(self,pid):
		form = self.pool.get('project.review.jingyingshishenpi.form')
		form_ids = form.search(self.cr,self.uid,[('project_id','=',pid),('state','=','accepted')])
		if form_ids:
			return form.browse(self.cr,self.uid,form_ids[0])	
	def _get_zongshishishenpi_form(self,pid):
		form = self.pool.get('project.review.zongshishishenpi.form')
		form_ids = form.search(self.cr,self.uid,[('project_id','=',pid),('state','=','accepted')])
		if form_ids:
			return form.browse(self.cr,self.uid,form_ids[0])	
	def _get_suozhangqianzishenpi_form(self,pid):
		form = self.pool.get('project.review.suozhangqianzishenpi.form')
		form_ids = form.search(self.cr,self.uid,[('project_id','=',pid),('state','=','accepted')])
		if form_ids:
			return form.browse(self.cr,self.uid,form_ids[0])	
	# def _get_suozhangshenpi_form(self,pid):
	# 	form = self.pool.get('project.review.suozhangshenpi.form')
	# 	form_ids = form.search(self.cr,self.uid,[('project_id','=',pid),('state','=','accepted')])
	# 	if form_ids:
	# 		return form.browse(self.cr,self.uid,form_ids[0]).reviewer_id.name
	# 	else:
	# 		return ''
report_sxw.report_sxw('report.project.renwuxiada','project.project',
	'oeaddon/updis/report/renwuxiada.rml',parser=renwuxiada,header=True
	)
		