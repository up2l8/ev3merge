
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import os

import ev3_merge
import webapp2
import jinja2

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        context = {}
        #self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(template.render(context))

app = webapp2.WSGIApplication([('/', MainPage),], debug=True)
