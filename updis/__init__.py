import hr
import hr_department
import document_page
import project
import internal_home_menu

from . import http
from . import controllers
from . import report

wsgi_postload = http.wsgi_postload
