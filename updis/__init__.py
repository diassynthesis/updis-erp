import hr
import hr_department
import document_page
import project
import internal_home_menu

from . import http
from . import controllers
from . import report

wsgi_postload = http.wsgi_postload

from tools.config import config
import report
import os

import reportlab.pdfbase.pdfmetrics
import reportlab.pdfbase.ttfonts
adp = os.path.abspath(config['addons_path']).split(',')[-1]
fntp = os.path.join(adp, 'updis', 'fonts', 'DejaVuSans.ttf')
reportlab.pdfbase.pdfmetrics.registerFont(reportlab.pdfbase.ttfonts.TTFont("DejaVu Sans",fntp))