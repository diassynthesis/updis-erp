import time
from report import report_sxw

class renwuxiada(report_sxw.rml_parse):
	"""docstring for renwuxiada"""
	def __init__(self, cr,uid,name,context):
		super(renwuxiada,self).__init__(cr,uid,name,context)
		self.localcontext.update({
			'time':time,
			})
report_sxw.report_sxw('report.project.renwuxiada','project.project',
	'oeaddon/updis/report/renwuxiada.rml',parser=renwuxiada,header=True
	)
		