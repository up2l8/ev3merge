
#vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
import os

from ev3 import Ev3
import webapp2
import jinja2
import zipfile
import StringIO
import cgi

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        context = {}
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(template.render(context))

    def post(self):
	upload_files = self.request.POST.multi.getall('file')
	base_file = upload_files.pop()
        name, _ = os.path.splitext(base_file.filename)
	merged = Ev3(base_file.file, name=name)
	
	for upload_file in upload_files:
            name, _ = os.path.splitext(upload_file.filename)
	    merged.merge(Ev3(upload_file.file, name=name))

        self.response.headers['Content-type'] = 'application/octet-stream'
        self.response.headers['Content-Disposition'] = 'attachment; filename=merged.ev3'
	outfile = StringIO.StringIO()
	merged.write(outfile)
	outfile.seek(0)
        self.response.write(outfile.read())

app = webapp2.WSGIApplication([('/', MainPage),], debug=True)
