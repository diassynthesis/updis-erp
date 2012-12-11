import time
from report import report_sxw

class renwuxiada(report_sxw.rml_parse):
	"""docstring for renwuxiada"""
	def __init__(self, cr,uid,name,context):
		super(renwuxiada,self).__init__(cr,uid,name,context)
		self.localcontext.update({
			'time':time,
			'get_suozhangshenpi':self._get_suozhangshenpi_form
			})
	def _get_suozhangshenpi_form(self,pid):
		form = self.pool.get('project.review.suozhangshenpi.form')
		form_ids = form.search(self.cr,self.uid,[('project_id','=',pid),('state','=','accepted')])
		if form_ids:
			return form.browse(self.cr,self.uid,form_ids[0]).reviewer_id.name
		else:
			return ''
report_sxw.report_sxw('report.project.renwuxiada','project.project',
	'oeaddon/updis/report/renwuxiada.rml',parser=renwuxiada,header=True
	)
		