
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import os

import ev3_merge
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
        ev3files = [f.file for f in self.request.POST.multi.getall('file')]
        
        merged = ev3files[0]
        merged.read()
        merged.seek(0)

        self.response.headers['Content-type'] = 'application/octet-stream'
        self.response.headers['Content-Disposition'] = 'attachment; filename=merged.ev3'
        self.response.write(merged.read())
        

app = webapp2.WSGIApplication([('/', MainPage),], debug=True)
